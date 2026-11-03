# 2026-11-03: Permite crear una cadena para clasificar un mensaje y responder de acuerdo a la misma.
# 2026-11-03: Fecha creación

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI #Modelo
from langchain_core.prompts import PromptTemplate #Plantilla -> Prompt dinámico
from langchain_core.output_parsers import StrOutputParser #Parsea la respuesta y la transforma en solo textos
from langchain_core.runnables import (RunnableBranch, RunnablePassthrough) #Bifurcaciones/Branches/Ramificaciones

load_dotenv()

modelo = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite") #gemini-3.6-flash

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

# Queioro ejecutar el paso de clasificación para obtener la respuesta de clasificación y convervar también la respuesta 
cadena_enrutamiento = (
    RunnablePassthrough.assign(clasificacion=paso_clasificacion) # Permite mantener el mensaje original y agrega un campo adicional con la clasificación
    | bifurcacion
)

print("Ejecutando clasificación y enrutamiento de mensaje...")
respuesta = cadena_enrutamiento.invoke({"mensaje": "Cuál es el sistema operaivo que usan para el sistema mac"})
print(respuesta) # Devuelve un diccionario con la clasificación y la respuesta generada por el modelo

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