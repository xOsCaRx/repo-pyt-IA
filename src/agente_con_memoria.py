# Herramientas personalizadas e introducción a la memoria 
# 2026-11-06 Fecha de creación

from dotenv import load_dotenv
from langchain_core.chat_history import InMemoryChatMessageHistory # Crear el historial en base a la sesión
from langchain_core.runnables.history import RunnableWithMessageHistory # Encapsula el agente para que implemente la memoria
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder # Chat prompt remplate son las plantilla pero incluyen system instruccion, place holder anota el ciclo react reazoning y acting
from langchain_core.runnables import RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import (
    AgentExecutor,
    create_tool_calling_agent
)
from pydantic import BaseModel, Field, ValidationError

load_dotenv()
modelo = ChatGoogleGenerativeAI(model="gemini-3.6-flash")

class ArgumentosConsultaEnvio(BaseModel):
    # Esquema para documentar y validar argumentos campo por campo ante el LLM

    numero_seguimiento: str = Field(description="Número de seguimiento del envío, por ejemplo 'AR123450'")
    incluir_historial: bool = Field(
        default = False,
        description = "Si es True incluye historial completo de los estados, no solo el actual"
    )

ESTADOS = {
    "AR12345" : {
        "actual" : "En tránsito, entrega estimada en 2 días",
        "historial" : [
            "Recibido en depósito",
            "En tránsito"
        ]
    },
    "AR12346" : {
        "actual" : "Entregado",
        "historial" : [
            "Recibido en depósito",
            "En tránsito"
        ]
    }
}

# Herramientas
# @tool(n"nuevo nombre") #puedo poner otro nombre distinto al de la función 
@tool(args_schema=ArgumentosConsultaEnvio) # LangChain transforma esta clase en un esquema JSON que se envía al LLM. El modelo lo lee textualmente
def consultar_estado_envio_detallado(numero_seguimiento: str, incluir_historial: bool = False):
    """ Consulta el estado de un envío con la opción de incluir el historial completo
     Consultar BDD con el num_seguimiento
     si no encuentro -> no se encontró
    """
    envio = ESTADOS.get(numero_seguimiento)
    if envio is None:
        return f"No se encontró un envío con el código: {numero_seguimiento}."

    if not incluir_historial:
        return envio["actual"]

    historial = ", ".join(envio["historial"]) #Recibido en depósito, en traánsito
    return f"{envio['actual']} (historial: {historial})"

@tool
def calcular_costo_envio(peso_kg: float, distancia_km: float) -> str:
    """Calcula el costo estimado de un envío según su peso y la distancia a recorrer.
    Usar cuando el usuario pregunta cuánto va a costar enviar algo."""
    costo = 500 + (peso_kg * 120) + (distancia_km * 3)
    return f"El costo estimado es de ${costo:.2f}"

# Listado de herramientas
herramientas = [consultar_estado_envio_detallado, calcular_costo_envio]

# Gestión de historial de memoria
historiales = {}

def obtener_historial(session_id: str):
    if session_id not in historiales:
        historiales[session_id] = InMemoryChatMessageHistory()
    return historiales[session_id]


prompt_agente = ChatPromptTemplate.from_messages([
    ("system", "Eres un asistente de logística que responde pregtunas usando las herramientas disponibles."),
    ("human", "{entrada}"),
    MessagesPlaceholder("agent_scratchpad")
])

agente = create_tool_calling_agent(modelo, herramientas, prompt_agente)

ejecutor_agente = AgentExecutor(
    agent = agente,
    tools = herramientas,
    verbose = True
)

if __name__ == "__main__":
    resultado = ejecutor_agente.invoke({"entrada" : "¿Cuál es el estado del envío AR12345, con su historial?"})
    print("Respuesta: ", resultado["output"][0]["text"])