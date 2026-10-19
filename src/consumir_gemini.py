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
    if not pregunta: raise ValueError("La pregunta no puede estar vacía.")
    url = f"{URL_BASE}{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    body = { "contents": [{ "parts": [{ "text": pregunta }] }] }
    return url, body

#Enviar petición
def enviar_peticion(url, body):
    try:
        response = requests.post(url, json=body)
    except requests.exceptions.ConnectionError:
        raise RuntimeError("No se pudo conectar con el servicio. Itente nuevamente más tarde.")
    except requests.exceptions.Timeout:
        raise RuntimeError("La solicitud ha excedido el tiempo de espera. Intente nuevamente más tarde.")

    if response.status_code != 200:
        raise RuntimeError(f"Error en la solicitud: {response.status_code} - {response.text}")
    try:
        return response.json()
    except requests.exceptions.JsonDecodeError:
        raise RuntimeError("La respuesta del serivio no llegó en el formato esperado.")

#Extraer respuesta
def extraer_texto(datos):
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError("Error al extraer el texto de la respuesta.")    

#Obtener respuesta
def obtener_respuesta(pregunta):
    url, body = armar_peticion(pregunta)
    datos = enviar_peticion(url, body)
    return extraer_texto(datos)

try:
    print(obtener_respuesta(input("Ingrese su pregunta: ")))     
except (ValueError, RuntimeError) as e:
    print(f"No se pudo completar la operación: {e}")