# 2026-11-04: Actividad core, enrutamiento con fallback adaptado a proyecto personal. 
# 2026-11-04: Fecha creación

import logging
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnablePassthrough, RunnableLambda

logging.basicConfig(
    filename='error.log', 
    level=logging.WARNING, 
    format='%(asctime)s - [%(levelname)s] %(name)s: %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S",
    filemode='a', # a de append, w de write (sobreescribe el archivo cada vez que se ejecuta)
    encoding='utf-8',
    force=True
)
logger = logging.getLogger(__name__)
load_dotenv()
modelo = ChatGoogleGenerativeAI(model="gemini-3.6-flash")

MENSAJE_ERR_GENERICO = ("No fue posible analizar el proyecto en este momento. Intenta nuevamente más tarde.")

def fallback_con_log(datos):
    logger.warning("La cadena principal falló. Activando fallback.")
    return MENSAJE_ERR_GENERICO

def construir_cadena_con_enrutamiento(
    paso_clasificacion=None,
    cadena_riesgos=None,
    cadena_decisiones=None,
    cadena_recuperacion=None
):
    if paso_clasificacion is None:
        plantilla_clasificacion = PromptTemplate.from_template(
            "Clasifica la solicitud de gestión de proyectos en una sola palabra: "
            "RIESGOS, DECISIONES o RECUPERACION. "
            "Responde solo con una de esas tres palabras.\nSolicitud: {mensaje}"
        )
        paso_clasificacion = (plantilla_clasificacion | modelo | StrOutputParser() | (lambda texto: texto.strip().upper()))

    if cadena_riesgos is None:
        cadena_riesgos = (PromptTemplate.from_template(
                "Actúa como analista de riesgos de proyectos de software. "
                "Identifica hasta tres riesgos, su evidencia y su impacto potencial. "
                "Distingue hechos de inferencias y no inventes datos.\nSolicitud: {mensaje}"
            ) | modelo | StrOutputParser()
        )

    if cadena_decisiones is None:
        cadena_decisiones = (
            PromptTemplate.from_template(
                "Actúa como consultor de decisiones de proyectos de software. "
                "Compara alternativas, ventajas y desventajas, y recomienda una acción "
                "solo cuando existan datos suficientes.\nSolicitud: {mensaje}"
            ) | modelo | StrOutputParser()
        )

    if cadena_recuperacion is None:
        cadena_recuperacion = (
            PromptTemplate.from_template(
                "Actúa como especialista en recuperación de proyectos de software. "
                "Propón hasta tres acciones priorizadas y métricas de seguimiento. "
                "No inventes plazos ni recursos disponibles.\nSolicitud: {mensaje}"
            ) | modelo | StrOutputParser()
        )

    bifurcacion = RunnableBranch(
        (lambda x: x["clasificacion"] == "RIESGOS", cadena_riesgos),
        (lambda x: x["clasificacion"] == "DECISIONES", cadena_decisiones),
        (lambda x: x["clasificacion"] == "RECUPERACION", cadena_recuperacion),
        RunnableLambda(lambda x: "No se pudo clasificar la solicitud del proyecto."),
    )

    return RunnablePassthrough.assign(clasificacion=paso_clasificacion) | bifurcacion


def construir_cadena_segura(cadena_principal):
    return cadena_principal.with_fallbacks([RunnableLambda(fallback_con_log)])


def crear_cadenas():
    cadena_principal = construir_cadena_con_enrutamiento()
    return construir_cadena_segura(cadena_principal)


def procesar_consulta_segura(cadena, mensaje):
    try:
        return cadena.invoke({"mensaje": mensaje})
    except Exception:
        logger.exception("Error al procesar la consulta")
        return MENSAJE_ERR_GENERICO


if __name__ == "__main__":
    consulta = (
        "El proyecto debía llevar un 80 % de avance y lleva 60 %. "
        "Quedan cuatro semanas. ¿Qué riesgos debemos priorizar?"
    )
    cadena_robusta = crear_cadenas()
    print(procesar_consulta_segura(cadena_robusta, consulta))
