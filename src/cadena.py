# Fecha creación 2026-11-02

from dotenv import load_dotenv
import os 
from langchain_google_genai import ChatGoogleGenerativeAI # Creo el modelo al que me quiero conectar 
from langchain_core.prompts import PromptTemplate # Me permite crear una plantilla
from langchain_core.output_parsers import StrOutputParser # Permite obtener la salida en un formato específico
from langchain_core.prompts import ChatPromptTemplate # Me permite crear un prompt de chat, que es un tipo de prompt que se utiliza para interactuar con modelos de lenguaje en un formato de conversación. Además ya incluye el rol de sistema o instrucción

load_dotenv()

# f-string Crea un formato y reemplaza el parámetro con el texto que deseo utilizar
plantilla = PromptTemplate.from_template("Explica el concepto de {tema} en un párrafo, para alguien que recién comienza en {area}")
plantilla_con_rol = ChatPromptTemplate.from_messages([
    ("system", "Eres un experto en el área de {area}, explica los conceptos de manera clara, simple y concisa."),
    ("user", "Explica el concepto de {tema} en un párrafo, para alguien que recién comienza en {area}") # Acá puedo usar human en vez de user
])

def main():
    modelo = ChatGoogleGenerativeAI(model="gemini-3.6-flash")
    # prompt = plantilla.invoke(
    #     {
    #         "tema" : "tokenización",
    #         "area" : "procesamiento de texzto"
    #     })

    #respuesta = modelo.invoke("¿Qué es un token?")
    #print(respuesta.content)
    #print(prompt.text)
    cadena_simple = plantilla | modelo | StrOutputParser() # StrOutputParser me permite recibir la respuesta en un formato de texto simple, sin metadatos ni información adicional
    respuesta = cadena_simple.invoke(
        {
            "tema" : "embeddings",
            "area" : "búsqueda semántica"
        })
    print(respuesta)

if __name__ == "__main__":
    main()
