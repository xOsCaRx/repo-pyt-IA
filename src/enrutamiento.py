# 2026-11-04: Se agrega RunnableLamba y se crea un flujo de respaldo para cuando el LLM no responde correctamente. Además creamos un file de error
# 2026-11-03: Permite crear una cadena para clasificar un mensaje y responder de acuerdo a la misma.
# 2026-11-03: Fecha creación

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI #Modelo
from langchain_core.prompts import PromptTemplate #Plantilla -> Prompt dinámico
from langchain_core.output_parsers import StrOutputParser #Parsea la respuesta y la transforma en solo textos
from langchain_core.runnables import (RunnableBranch, RunnablePassthrough, RunnableLambda) #Bifurcaciones/Branches/Ramificaciones
import logging # Generar un archivo de log para registrar errores y eventos importantes

logging.basicConfig(
    filename='error.log', 
    level=logging.WARNING, 
    format='%(asctime)s - [%(levelname)s] %(name)s: %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S",
    filemode='a', # a de append, w de write (sobreescribe el archivo cada vez que se ejecuta)
    encoding='utf-8',
    force=True
)
load_dotenv()

modelo = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite") #gemini-3.6-flash

def fallback_con_log(x):
    logging.warning("Cadena principal falló. Activando respuesta genérica")
    return "Lo siento, no puedo procesar tu solicitud en este momento. Un miembro de nuestro equipo te contactará en breve."

def crear_cadenas():
    plantilla_clasificacion = PromptTemplate.from_template("""
        Clasifica el siguiente mensaje de soporte en una sola palabra:
        pregunta, queja o sugerencia. Responde solo con una de esas palabras.
        mensaje: {mensaje}"""
    )

    paso_clasificacion = (
        plantilla_clasificacion 
        | modelo 
        | StrOutputParser()
        | (lambda texto: texto.strip().lower() )
        )

    cadena_pregunta =(
        PromptTemplate.from_template("Responde esta pregtuna técnica con precisión: {mensaje}")
        | modelo 
        | StrOutputParser()
    )

    cadena_queja =(
        PromptTemplate.from_template("Responde esta queja de manera empática, reconociendo el problema antes de ofrecer la solución: {mensaje}")
        | modelo 
        | StrOutputParser()
    )

    cadena_sugerencia =(
        PromptTemplate.from_template("Responde esta sugerencia de manera positiva, agradeciendo la retroalimentación y ofreciendo una solución: {mensaje}")
        | modelo 
        | StrOutputParser()
    )

    bifurcacion = RunnableBranch(
        (lambda x: x["clasificacion"] == "sugerencia", cadena_sugerencia), # if
        (lambda x: x["clasificacion"] == "queja", cadena_queja), # else if
        cadena_pregunta # else 
    ) 

    # Quiero ejecutar el paso de clasificación para obtener la respuesta de clasificación y convervar también la respuesta 
    cadena_enrutamiento = (
        RunnablePassthrough.assign(clasificacion=paso_clasificacion) # Permite mantener el mensaje original y agrega un campo adicional con la clasificación
        | bifurcacion
    )

    #Fallback: cadena de respaldo. Captura las caídas de mi LLM (ratelimiterror, 401, apiconectionerror, etc) y permite ejecutar un flujo alternativo.

    respuesta_generica = RunnableLambda(
        fallback_con_log
    )

    cadena_robusta = cadena_enrutamiento.with_fallbacks([respuesta_generica])
    return cadena_robusta

def procesar_mensaje_seguro(cadena, mensaje):
    try:
        return cadena.invoke({"mensaje": mensaje})
    except Exception as e:
        logging.error(f"Error al procesar el mensaje: {e}")
        return "Lo siento, no puedo procesar tu solicitud en este momento. Inténtalo más tarde."

if __name__ == "__main__":
    mensaje_prueba = "Mi teléfono no está funcionando."
    cadena_robusta = crear_cadenas()
    print("Ejecutando clasificación y enrutamiento de mensaje...")
    respuesta_segura = procesar_mensaje_seguro(cadena_robusta, mensaje_prueba)
    print(f"Respuesta segura: {respuesta_segura}")


# respuesta = cadena_robusta.invoke({"mensaje": "Cuál es el sistema operaivo que usan para el sistema mac"})
# print(respuesta) # Devuelve un diccionario con la clasificación y la respuesta generada por el modelo


# caminos = RunnableBranch(
#     (condicion_1, rama_1), # if
#     (condicion_2, rama_2), # else if
#     (condicion_3, rama_3), # else if
#     rama_por_defecto # else
#     ) # Cada condición debe ser una función, suele ser un lambda
# )


# mensaje_prueba ="Mi teléfono no está funcionando."

# clasificacion = paso_clasificacion.invoke({"mensaje": mensaje_prueba})

# print(f"Clasificación: {clasificacion}")    