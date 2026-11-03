# Fecha creación 2026-11-02
# Ejercicio práctico de cadena de tres pasos 
# 1. Leer texto y devolver ideas centrales 
# 2. Luego reformular la salida para que se ajuste a una audiencia en específico
# 3. Formatear como una lista de viñetas 

from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI # Creo el modelo al que me quiero conectar 
from langchain_core.prompts import PromptTemplate # Me permite crear una plantilla
from langchain_core.output_parsers import StrOutputParser # Permite obtener la salida en un formato específico
from langchain_core.prompts import ChatPromptTemplate # Me permite crear un prompt de chat, que es un tipo de prompt que se utiliza para interactuar con modelos de lenguaje en un formato de conversación. Además ya incluye el rol de sistema o instrucción

load_dotenv()

modelo = ChatGoogleGenerativeAI(model="gemini-3.6-flash")

plantilla_ideas = PromptTemplate.from_template("Extrae las ideas centrales del siguiente texto: {texto}")
plantilla_reformulacion = PromptTemplate.from_template("Reformula el siguiente texto para que sea comprensible para alguien sin conocimiento técnico: {texto}")
plantilla_formateo = PromptTemplate.from_template("Formatea el siguiente texto como una lista de viñetas markdown de máximo 3 líneas, sin introcucción: {texto}")

paso_ideas = plantilla_ideas | modelo | StrOutputParser()
paso_reformulacion = plantilla_reformulacion | modelo | StrOutputParser()
paso_formateo = plantilla_formateo | modelo | StrOutputParser()

texto_entrada = "Los modelos de lenguaje grandes generan texto "
"prediciendo un token a la vez, basándose en el "
"texto que ya generaron antes. Cada token puede "
"ser una palabra completa, parte de una palabra, "
"o un signo de puntuación. Antes de que el modelo "
"genere una respuesta, el texto de entrada se "
"divide en tokens, un proceso llamado tokenización."

ideas = paso_ideas.invoke({"texto": texto_entrada})
reformulacion = paso_reformulacion.invoke({"texto": ideas})
formateo = paso_formateo.invoke({"texto": reformulacion})

def main():
    # print("Iniciando cadena de tres pasos...")
    # print("Ideas centrales:")
    # print(ideas)
    # print("\nReformulación:")
    # print(reformulacion)
    # print("\nFormateo:")
    print(formateo)

if __name__ == "__main__":
    main()
