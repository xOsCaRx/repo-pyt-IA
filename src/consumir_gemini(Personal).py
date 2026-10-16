import os
import requests
from dotenv import load_dotenv

#Función que permite cargar secretos y configuraciones desde .env
load_dotenv()

#Contruiyo el cuerpo de la solicitud
def build_request_and_call(question):
    api_key = os.getenv("GEMINI_API_KEY")
    model = "gemini-flash-latest"
    body = { "contents": [{ "parts": [{ "text": question }] }] }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    return  requests.Request("POST", url, json=body)

#realizo la llamada a la API
def call_api(question):
    request = build_request_and_call(question)
    session = requests.Session()
    return session.send(request.prepare()) 

#Extraigo la respuesta de la API
def extract_answer(response):
    return response.json()['candidates'][0]['content']['parts'][0]['text']

#Pregunto a la API y obtengo la respuesta
response = call_api("¿Cuál es la capital de Chile?")
print(extract_answer(response))