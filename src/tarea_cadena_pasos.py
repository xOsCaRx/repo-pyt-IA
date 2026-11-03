# 2026-11-03: Fecha creación
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

modelo = ChatGoogleGenerativeAI(model="gemini-3.6-flash")

# PASO 1: Extraer hechos objetivos del proyecto
plantilla_hechos = PromptTemplate.from_template(
    """
    ROL:Actúa como analista de gestión de proyectos de software. 
    OBJETIVO: Extrae los hechos verificables del informe.
    INSTRUCCIONES: Identifica y enumera los hechos objetivos del proyecto, incluyendo fechas, porcentajes, cifras y cualquier información verificable.
    RESTRICCIONES:
    1. Usa solamente la información proporcionada.
    2. Conserva las cifras y fechas originales.
    3. No inventes información.
    4. Si falta información relevante, indícalo.
    5. Entrega una lista breve de hechos y datos faltantes.
    INFORME:
    {texto}
    """
)

# PASO 2: Identificar riesgos
plantilla_riesgos = PromptTemplate.from_template(
    """
    ROL: Actúa como especialista en riesgos de proyectos de software. 
    OBJETIVO:Analiza los hechos recibidos e identifica hasta 3 riesgos relevantes para el cumplimiento del proyecto.
    INSTRUCCIONES: Para cada riesgo indica:
    1. Descripción.
    2. Posible impacto.
    3. Evidencia que lo fundamenta.
    RESTRICCIONES:
    1. Distingue los hechos de los riesgos inferidos.
    2. No inventes probabilidades, fechas ni impactos numéricos.
    HECHOS DEL PROYECTO:
    {texto}
    """
)

# PASO 3: Proponer acciones de mitigación
plantilla_acciones = PromptTemplate.from_template(
    """
    ROL: Actúa como consultor senior de gestión de proyectos. 
    OBJETIVO: A partir de los riesgos identificados, propone hasta 3 acciones concretas y priorizadas.
    INSTRUCCIONES:Para cada acción indica:
    1. Prioridad.
    2. Acción recomendada.
    3. Justificación.
    4. Resultado esperado.
    RESTRICCIONES: 
    1. No garantices resultados ni inventes recursos disponibles.
    2. Indica qué información falta para validar las acciones.
    RIESGOS IDENTIFICADOS:
    {texto}
    """
)

# PASO 4: Preparar informe ejecutivo
plantilla_informe = PromptTemplate.from_template(
    """
    ROL: Actúa como asesor de un comité ejecutivo.
    OBJETIVO:Prepara un informe breve para apoyar la toma de decisiones, utilizando exclusivamente la información recibida.
    INSTRUCCIONES: Organiza la respuesta en estas secciones:
    1. Resumen ejecutivo
    2. Riesgos que requieren atención
    3. Acciones recomendadas
    4. Información pendiente de validar
    RESTRICCIONES:
    1. Máximo 250 palabras.
    2. No agregues hechos ni cifras que no estén en el análisis.
    ANÁLISIS Y RECOMENDACIONES:
    {texto}
    """
)

# INFORME INICIAL DE PROYECTO
texto_entrada = """
Proyecto de desarrollo de una aplicación de gestión de clientes.
Avance planificado: 80%.
Avance real: 60%.
Presupuesto consumido: 85%.
Tiempo restante: 4 semanas.
Equipo: 6 desarrolladores.
Dos desarrolladores estarán ausentes durante las próximas
2 semanas.
Existe una integración crítica con un proveedor que lleva
10 días bloqueada.
"""

def construir_cadena(modelo):
    paso_hechos = plantilla_hechos | modelo | StrOutputParser()
    paso_riesgos = plantilla_riesgos | modelo | StrOutputParser()
    paso_acciones = plantilla_acciones | modelo | StrOutputParser()
    paso_informe = plantilla_informe | modelo | StrOutputParser()

    cadena_cuatro_pasos = (
        paso_hechos
        | (lambda texto: {"texto": texto})
        | paso_riesgos
        | (lambda texto: {"texto": texto})
        | paso_acciones
        | (lambda texto: {"texto": texto})
        | paso_informe
    )

    return cadena_cuatro_pasos


def main():
    print("Iniciando análisis del proyecto...")

    cadena = construir_cadena(modelo)    
    respuesta = cadena.invoke(
        {"texto": texto_entrada}
    )

    print("\nINFORME EJECUTIVO")
    print("=" * 60)
    print(respuesta)


if __name__ == "__main__":
    main()
