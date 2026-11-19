# 2026-11-19 Utilizo librería rich para ver mejor los resultados. Instalar con: pip3 install rich
# 2026-11-19 Creación. Permite cargar en una base vectorial información reevante al proyecto de prueba. El texto del proyecto lo cree con IA 

import os
import shutil
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from rich import print

load_dotenv()

CARPETA_DB = "vectorstore_core"
ARCHIVO_DATOS = "proyecto_atlas.txt"
MODELO_EMBEDDINGS = "models/gemini-embedding-001"


def cargar_vectorstore(carpeta_db):
    """Abre una colección Chroma que ya está guardada en disco."""
    embeddings = GoogleGenerativeAIEmbeddings(model=MODELO_EMBEDDINGS)
    return Chroma(persist_directory=carpeta_db, embedding_function=embeddings)


def formatear_contexto(chunks):
    """Entrega el contexto numerado y un diccionario de fuentes."""
    textos = []
    citas = {}

    for numero, documento in enumerate(chunks, start=1):
        fuente = documento.metadata.get("fuente", "fuente desconocida")
        textos.append(f"[{numero}] Fuente: {fuente}\n{documento.page_content}")
        citas[str(numero)] = fuente

    return "\n\n".join(textos), citas


def indexar_documentos():
    if os.path.exists(CARPETA_DB):
        print(f"[yellow]La carpeta '{CARPETA_DB}' ya existe.[/yellow]")
        return

    with open(ARCHIVO_DATOS, "r", encoding="utf-8") as archivo:
        contenido = archivo.read()

    secciones = contenido.split("\n---\n")
    documentos = []

    for numero, seccion in enumerate(secciones, start=1):
        seccion = seccion.strip()
        if seccion:
            titulo = seccion.split("\n")[0]
            documentos.append(Document(
                page_content=seccion,
                metadata={"fuente": f"{ARCHIVO_DATOS} - {titulo}", "seccion": numero}
            ))

    embeddings = GoogleGenerativeAIEmbeddings(model=MODELO_EMBEDDINGS)
    Chroma.from_documents(
        documents=documentos,
        embedding=embeddings,
        persist_directory=CARPETA_DB
    )
    print(f"[green]Indexación terminada: {len(documentos)} secciones guardadas en '{CARPETA_DB}'.[/green]")


if __name__ == "__main__":
    indexar_documentos()
