import os
import requests
from dotenv import load_dotenv

#Función que permite cargar secretos y configuraciones desde .env
load_dotenv()

#Constantes
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-flash-latest"
URL_BASE = f"https://generativelanguage.googleapis.com/v1beta/models/"

#Crear solicitud
def armar_peticion(pregunta):
    url = f"{URL_BASE}{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    body = { "contents": [{ "parts": [{ "text": pregunta }] }] }
    return url, body

#Enviar petición
def enviar_peticion(url, body):
    response = requests.post(url, json=body)
    return response.json()

#Extraer respuesta
def extraer_texto(datos):
    return datos["candidates"][0]["content"]["parts"][0]["text"]

def obtener_respuesta(pregunta):
    url, body = armar_peticion(pregunta)
    datos = enviar_peticion(url, body)
    return extraer_texto(datos)
     
print(obtener_respuesta("¿Cuál es la capital de Chile?"))