# 2026-11-18 Creación. Script para comprobar latencia y costo

import time
import json
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from rich import print

from rag_indexer import cargar_vectorstore, formatear_contexto

load_dotenv()

MODELO = "gemini-3.5-flash-lite"
CARPETA_DB = "vectorstore_core"  
ARCHIVO_REGISTROS = "registros_latencia_costo.jsonl"
TARIFA_ENTRADA_X1M = 0.30
TARIFA_SALIDA_X1M = 2.50

PROMPT_TEMPLATE = """Responde la pregunta usando solo el contexto de abajo.
Cita la fuente de cada afirmación con su número entre corchetes, como [1].
Si el contexto no alcanza para responder, dilo explícitamente en vez de inventar.

Contexto:
{contexto}

Pregunta: {pregunta}

Respuesta:"""


@contextmanager
def medir(tiempos: dict, etapa: str):
    """Mide en segundos el bloque dentro de 'with medir(...)'."""
    inicio = time.perf_counter()
    try:
        yield
    finally:
        tiempos[etapa] = time.perf_counter() - inicio


def calcular_costo(tokens_entrada: int, tokens_salida: int,
                   tarifa_entrada_x1M: float = TARIFA_ENTRADA_X1M,
                   tarifa_salida_x1M: float = TARIFA_SALIDA_X1M) -> float:
    """Estima el costo USD de tokens de generación, no de todo el flujo RAG."""
    costo_entrada = (tokens_entrada / 1000000) * tarifa_entrada_x1M
    costo_salida = (tokens_salida / 1000000) * tarifa_salida_x1M
    return round(costo_entrada + costo_salida, 8)


def registrar_consulta(vector_store, pregunta: str, k: int = 3) -> dict:
    """Consulta RAG real y obtiene tiempos por etapa y tokens reales."""
    tiempos = {}
    chat_model = ChatGoogleGenerativeAI(model=MODELO)

    with medir(tiempos, "embed_y_busqueda"):
        retriever = vector_store.as_retriever(search_kwargs={"k": k})
        chunks = retriever.invoke(pregunta)

    with medir(tiempos, "armado_prompt"):
        contexto, citas = formatear_contexto(chunks)
        prompt = PROMPT_TEMPLATE.format(contexto=contexto, pregunta=pregunta)

    with medir(tiempos, "generacion"):
        respuesta = chat_model.invoke(prompt)

    tokens_reales = dict(respuesta.usage_metadata) if respuesta.usage_metadata else None
    costo_usd = None
    if tokens_reales:
        if tokens_reales.get("input_tokens") is not None and tokens_reales.get("output_tokens") is not None:
            costo_usd = calcular_costo(
                tokens_entrada=tokens_reales["input_tokens"],
                tokens_salida=tokens_reales["output_tokens"]
            )

    factor_crecimiento = round(len(prompt) / len(pregunta), 1) if pregunta else None

    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "modelo": MODELO,
        "pregunta": pregunta,
        "k": k,
        "chunks_recuperados": len(chunks),
        "respuesta_generada": respuesta.content,
        "citas_disponibles": citas,
        "tiempos_ms": {etapa: round(seg * 1000, 2) for etapa, seg in tiempos.items()},
        "tiempo_total_ms": round(sum(tiempos.values()) * 1000, 2),
        "factor_crecimiento": f"{factor_crecimiento}x" if factor_crecimiento is not None else None,
        "tokens": tokens_reales,
        "costo_estimado_generacion_usd": costo_usd,
        "tarifa_ejemplo_entrada_usd_1M": TARIFA_ENTRADA_X1M,
        "tarifa_ejemplo_salida_usd_1M": TARIFA_SALIDA_X1M
    }
    return registro


def guardar_registro(registro: dict) -> None:
    """Agrega una línea JSON real por consulta completada."""
    with open(ARCHIVO_REGISTROS, "a", encoding="utf-8") as archivo:
        archivo.write(json.dumps(registro, ensure_ascii=False, default=str) + "\n")


if __name__ == "__main__":
    vs = cargar_vectorstore(CARPETA_DB)

    preguntas = [
        "¿Cuál es el estado de avance del proyecto y qué actividades están pendientes?",
        "¿Qué riesgos o bloqueos están registrados para el proyecto?",
        "¿Qué información hay sobre presupuesto y recursos del proyecto?"
    ]

    # Tres preguntas distintas con k=3, más la primera con k=6.
    pruebas = [
        (preguntas[0], 3),
        (preguntas[1], 3),
        (preguntas[2], 3),
        (preguntas[0], 6)
    ]

    for numero, (pregunta, k) in enumerate(pruebas, start=1):
        print(f"\n[bold]Prueba {numero}: k={k}[/bold] - {pregunta}")
        try:
            registro = registrar_consulta(vs, pregunta, k)
        except Exception as error:
            print(f"[red]La consulta falló: {error}[/red]")
            print("No se guardó un registro de éxito para esta consulta.")
            continue

        guardar_registro(registro)
        print(registro)
        print(f"[green]Registro guardado en {ARCHIVO_REGISTROS}[/green]")
