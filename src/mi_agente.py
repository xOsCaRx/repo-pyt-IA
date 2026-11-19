# 2026-11-18 Creación, agente para apoyo de actividades de gestión con human in the loop para acciones relevantes
from dotenv import load_dotenv
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from pydantic import BaseModel, Field
import queue
import threading
import json
from datetime import datetime, timezone

load_dotenv()
modelo = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")# gemini-3.6-flash

# Persistencia y trazabilidad: un registro JSON por línea.
def registrar_traza(session_id: str, entrada: str, resultado: dict) -> None:
    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "entrada": entrada,
        "acciones": [
            {
                "herramienta": accion.tool,
                "argumentos": accion.tool_input,
                "observacion": observacion
            }
            for accion, observacion in resultado.get("intermediate_steps", [])
        ],
        "respuesta_final": resultado.get("output", "")
    }
    with open("trazas_agente.jsonl", "a", encoding="utf8") as archivo:
        archivo.write(json.dumps(registro, ensure_ascii=False, default=str) + "\n")

# Human in the loop: Queue y Thread
registro_aprobaciones = []

def esperar_aprobacion(mensaje: str, tiempo_limite_seg: int = 30) -> bool:
    cola_respuesta = queue.Queue()

    def pedir_entrada():
        try:
            texto = input(mensaje)
            cola_respuesta.put(texto.strip().lower())
        except (EOFError, KeyboardInterrupt):
            cola_respuesta.put("")

    hilo = threading.Thread(target=pedir_entrada, daemon=True)
    hilo.start()
    try:
        respuesta = cola_respuesta.get(timeout=tiempo_limite_seg)
        return respuesta.lower() == "s"
    except queue.Empty:
        print("Tiempo de espera agotado. Solicitud rechazada.")
        return False


def registrar_aprobacion(herramienta: str, argumentos: dict, aprobado: bool) -> None:
    registro = {
        "herramienta": herramienta,
        "argumentos": argumentos,
        "aprobado": aprobado,
        "fecha_hora": datetime.now(timezone.utc).isoformat()
    }
    registro_aprobaciones.append(registro)
    with open("aprobaciones_agente.jsonl", "a", encoding="utf8") as archivo:
        archivo.write(json.dumps(registro, ensure_ascii=False) + "\n")

# Esquema de validación
class ArgumentosConsultaProyecto(BaseModel):
    codigo_proyecto: str = Field(description="Código de proyecto, por ejemplo PYT001")
    incluir_riesgos: bool = Field(default=False, description="Incluye los riesgos conocidos del proyecto")

# Data simulada
PROYECTOS = {
    "PYT001": {
        "nombre": "Plataforma de gestión de proyectos",
        "avance": 65,
        "estado": "En ejecución",
        "riesgos": ["Retraso en integración de datos", "Disponibilidad limitada del equipo"],
        "tareas": {"T001": "Pendiente", "T002": "En progreso"},
        "presupuesto_disponible": 1500000
    },
    "PYT002": {
        "nombre": "Tablero de indicadores",
        "avance": 90,
        "estado": "En ejecución",
        "riesgos": ["Validación pendiente con usuarios"],
        "tareas": {"T003": "En progreso"},
        "presupuesto_disponible": 500000
    }
}

# Riesgo bajo: solo lectura.
@tool(args_schema=ArgumentosConsultaProyecto)
def consultar_estado_proyecto(codigo_proyecto: str, incluir_riesgos: bool = False) -> str:
    """Consulta el estado y avance de un proyecto. Opcionalmente muestra sus riesgos."""
    proyecto = PROYECTOS.get(codigo_proyecto)
    if proyecto is None:
        return f"No se encontró el proyecto {codigo_proyecto}."
    respuesta = f"{proyecto['nombre']}: {proyecto['estado']}, avance {proyecto['avance']}%."
    if incluir_riesgos:
        respuesta += " Riesgos: " + "; ".join(proyecto["riesgos"])
    return respuesta

# Riesgo bajo: cálculo sin modificación de datos.
@tool
def calcular_costo_actividad(horas: float, tarifa_hora: float) -> str:
    """Calcula el costo estimado de una actividad con horas y tarifa por hora en CLP."""
    if horas < 0 or tarifa_hora < 0:
        return "No se pueden utilizar horas ni tarifas negativas."
    costo = horas * tarifa_hora
    return f"Costo estimado de la actividad: ${costo:.0f} CLP."

# Riesgo medio: escritura reversible
@tool
def actualizar_estado_tarea(codigo_proyecto: str, codigo_tarea: str, nuevo_estado: str) -> str:
    """Actualiza el estado de una tarea. Estados válidos: Pendiente, En progreso, Terminada."""
    proyecto = PROYECTOS.get(codigo_proyecto)
    if proyecto is None:
        return f"No se encontró el proyecto {codigo_proyecto}."
    if codigo_tarea not in proyecto["tareas"]:
        return f"No se encontró la tarea {codigo_tarea} en {codigo_proyecto}."
    if nuevo_estado not in ["Pendiente", "En progreso", "Terminada"]:
        return "Estado no válido. Opciones disponibles: Pendiente, En progreso o Terminada."
    estado_anterior = proyecto["tareas"][codigo_tarea]
    proyecto["tareas"][codigo_tarea] = nuevo_estado
    return f"Tarea {codigo_tarea}: estado anterior '{estado_anterior}', nuevo estado '{nuevo_estado}'."

# Riesgo alto: movimiento presupuestario.
@tool
def registrar_gasto_proyecto(codigo_proyecto: str, concepto: str, monto: float) -> str:
    """Registra un gasto presupuestario. Requiere aprobación humana antes de descontar el monto."""
    proyecto = PROYECTOS.get(codigo_proyecto)
    if proyecto is None:
        return f"No se encontró el proyecto {codigo_proyecto}."
    if monto <= 0:
        return "El monto debe ser mayor que cero."
    if monto > proyecto["presupuesto_disponible"]:
        return "Fondos insuficientes. No se registra el gasto."

    argumentos = {"codigo_proyecto": codigo_proyecto, "concepto": concepto, "monto": monto}
    mensaje = (f"[APROBACIÓN HUMANA] ¿Registrar gasto de ${monto:.0f} CLP "
               f"en {codigo_proyecto}, concepto '{concepto}'? s/n: ")
    aprobado = esperar_aprobacion(mensaje, tiempo_limite_seg=30)
    registrar_aprobacion("registrar_gasto_proyecto", argumentos, aprobado)
    if not aprobado:
        return "Gasto no autorizado. No se modificó el presupuesto."

    proyecto["presupuesto_disponible"] -= monto
    return (f"Gasto registrado por ${monto:.0f} CLP. "
            f"Presupuesto disponible: ${proyecto['presupuesto_disponible']:.0f} CLP.")

herramientas = [
    consultar_estado_proyecto,
    calcular_costo_actividad,
    actualizar_estado_tarea,
    registrar_gasto_proyecto
]

# HISTORIAL
historiales = {}

def obtener_historial(session_id: str):
    if session_id not in historiales:
        historiales[session_id] = InMemoryChatMessageHistory()
    return historiales[session_id]

prompt_agente = ChatPromptTemplate.from_messages([
    ("system", "Eres un asistente de gestión de proyectos. Usa exclusivamente las herramientas "
               "disponibles para consultar o modificar datos. No inventes estados, montos ni riesgos. "
               "Informa cuando un dato no existe. El registro de gastos requiere aprobación humana."
               ),
    MessagesPlaceholder("chat_history"),
    ("human", "{entrada}"),
    MessagesPlaceholder("agent_scratchpad")
])

agente = create_tool_calling_agent(modelo, herramientas, prompt_agente)
ejecutor_agente = AgentExecutor(
    agent=agente,
    tools=herramientas,
    verbose=True,
    return_intermediate_steps=True
)

limpiar_salida = RunnableLambda(
    lambda d: {**d, "output": d["output"][0]["text"]
               if isinstance(d.get("output"), list) else d.get("output")}
)
cadena_agente = ejecutor_agente | limpiar_salida
agente_con_memoria = RunnableWithMessageHistory(
    cadena_agente,
    obtener_historial,
    input_messages_key="entrada",
    history_messages_key="chat_history",
    output_messages_key="output"
)

# Ejecutar una consulta y guardar su traza.
def ejecutar_consulta(entrada: str, session_id: str) -> None:
    config = {"configurable": {"session_id": session_id}}
    resultado = agente_con_memoria.invoke({"entrada": entrada}, config)
    print("\nRespuesta:", resultado["output"])
    registrar_traza(session_id, entrada, resultado)
    print("Traza guardada en trazas_agente.jsonl")

if __name__ == "__main__":
    print("1. Consultar avance y riesgos (bajo)")
    print("2. Calcular costo de actividad (bajo)")
    print("3. Actualizar estado de tarea (medio)")
    print("4. Registrar gasto simulado (alto; requiere aprobación)")
    opcion = input("Selecciona una opción (1-4): ").strip()
    if opcion == "1":
        ejecutar_consulta("Consulta el avance y los riesgos de PYT001.", "cliente_test")
    elif opcion == "2":
        ejecutar_consulta("¿Cuánto cuesta una actividad de 20 horas a 25000 CLP la hora?", "cliente_test")
    elif opcion == "3":
        ejecutar_consulta("Actualiza la tarea T001 de PYT001 al estado En progreso.", "cliente_test")
    elif opcion == "4":
        ejecutar_consulta("Registra un gasto de 100000 CLP en PYT001 por capacitación.", "cliente_test")
    else:
        print("Opción no válida.")
