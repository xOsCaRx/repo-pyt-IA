import os
import requests
from dotenv import load_dotenv
import time # Para contabilizar el tiempo
#----------------------------------------------------------------------------------------------------
# Función que permite cargar secretos y configuraciones desde .env
#----------------------------------------------------------------------------------------------------
load_dotenv()

#----------------------------------------------------------------------------------------------------
# Constantes
# Fecha de actualización: 2026-10-21
#----------------------------------------------------------------------------------------------------
GEMINI_URL_BASE = f"https://generativelanguage.googleapis.com/v1beta/models/"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-flash-latest"
GEMINI_PRECIO_ENTRADA = 0
GEMINI_PRECIO_SALIDA = 0
#----------------------------------------------------------------------------------------------------
# Crear solicitud
#----------------------------------------------------------------------------------------------------
def armar_peticion(pregunta):
    if not pregunta: raise ValueError("La pregunta no puede estar vacía.")
    url = f"{GEMINI_URL_BASE}{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    body = { "contents": [{ "parts": [{ "text": pregunta }] }] }
    return url, body

#----------------------------------------------------------------------------------------------------
# Enviar petición
#----------------------------------------------------------------------------------------------------
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
    except requests.exceptions.JSONDecodeError:
        raise RuntimeError("La respuesta del servicio no llegó en el formato esperado.")

#----------------------------------------------------------------------------------------------------
# Extraer respuesta: Permite extraer el texto de la respuesta de la API y calcular el costo de la misma.
# Última modificación: 2026-10-19
#----------------------------------------------------------------------------------------------------
def extraer_texto(datos):
    try:
        costo = calcular_costo(datos, precio_entrada=GEMINI_PRECIO_ENTRADA, precio_salida=GEMINI_PRECIO_SALIDA)
        return datos["candidates"][0]["content"]["parts"][0]["text"], costo
    except (KeyError, IndexError, TypeError):
        raise RuntimeError("Error al extraer el texto de la respuesta.")    

#----------------------------------------------------------------------------------------------------
# Obtener respuesta: Permite obtener la respuesta de la API 
# Última modificación: 2026-10-20
# 2026-10-20 : Se agregó la medición de latencia para evaluar el tiempo de respuesta de la API.
#----------------------------------------------------------------------------------------------------
def obtener_respuesta(pregunta):
    url, body = armar_peticion(pregunta)
    inicio_rqst = time.perf_counter() # Inicia el contador de tiempo
    datos = enviar_peticion(url, body)
    fin_rqst = time.perf_counter() # Finaliza el contador de tiempo
    latencia = fin_rqst - inicio_rqst
    return extraer_texto(datos), latencia

#----------------------------------------------------------------------------------------------------
# Calcular costo (tokens): Permite obtener el costo de la respuesta en función de los tokens utilizados en la entrada y salida.
# Creación: 2026-10-19
# Última modificación: 2026-10-19
#----------------------------------------------------------------------------------------------------
def calcular_costo(datos:dict, precio_entrada: float, precio_salida: float):
    try:
        usage = datos["usageMetadata"] # Sección JSON de la respuesta de la API
        prompt_token = int(usage.get("promptTokenCount", 0)) # Número de tokens utilizados en la entrada
        candidates_token = int(usage.get("candidatesTokenCount", 0)) # Número de tokens utilizados en la salida
        thought_token = int(usage.get("thoughtsTokenCount", 0)) # Número de tokens utilizados en el razonamiento
        costo_entrada = prompt_token * precio_entrada
        costo_salida = (candidates_token + thought_token) * precio_salida
        return costo_entrada + costo_salida
    except KeyError as error:
        raise ValueError(f"Falta un dato para poder calcular el costo: {error}") from error
    except (TypeError, ValueError) as error:
        raise ValueError("Los datos de tokens tienen un formato inválido.") from error

#----------------------------------------------------------------------------------------------------
# Main
# 2026-10-21 : Se agrega diccionario de modelos para poder iterar sobre ellos y comparar resultados.
#              Se fija la pregunta de manera estática para poder comparar resultados entre modelos.
# 2026-10-20 : Se agregó la medición de latencia para evaluar el tiempo de respuesta de la API.
#----------------------------------------------------------------------------------------------------
try:
    pregunta = "Actúa como un asesor experto en gestión de proyectos de software. Un proyecto tiene un avance planificado del 70%, pero su avance real es del 55%. Se ha consumido el 80% del presupuesto, quedan 6 semanas para la fecha de entrega y dos desarrolladores clave estarán ausentes durante las próximas 2 semanas. Analiza la situación e identifica los tres riesgos más importantes. Propón tres acciones correctivas, ordénalas por prioridad y explica el impacto esperado de cada una sobre el plazo, costo y alcance. Separa los hechos de tus inferencias y señala qué información adicional necesitas para fundamentar mejor las recomendaciones. No inventes datos."
    modelos = []
    modelos.append(["gemini-3.5-flash-lite", 0.0000003, 0.0000025])
    modelos.append(["gemini-3.6-flash", 0.00000075, 0.0000015])
    modelos.append(["gemini-3.8-flash", 0.00000075, 0.00000375])

    for i, modelo in enumerate(modelos): #Itera por los modelos definidos en la lista
        print(f"{i+1}. MODELO: {modelo[0]}")
        GEMINI_MODEL = modelo[0]  # Selecciona el modelo
        GEMINI_PRECIO_ENTRADA = modelo[1]  # Selecciona el precio de entrada
        GEMINI_PRECIO_SALIDA = modelo[2]  # Selecciona el precio de salida
        latencias = []
        costos = []
        for i in range(4):  # Realiza 4 iteraciones para cada modelo
            print("INICIO ITERACIÓN: ", i+1, "-------------------------")            
            (respuesta, costo), latencia = obtener_respuesta(pregunta)
            print(f"Respuesta: {respuesta}")
            print(f"Costo estimado de la respuesta: ${costo:.6f} USD")
            print(f"Latencia de la solicitud: {latencia:.4f} segundos")
            latencias.append(latencia)
            costos.append(costo)
            print("FIN ITERACIÓN: ", i+1 , "-------------------------")
        promedio_latencia = sum(latencias) / len(latencias)
        promedio_costo = sum(costos) / len(costos)
        print()
        print("------------------------------------------------------------")
        print(GEMINI_MODEL)
        print(f"Promedio de latencia de la solicitud: {promedio_latencia:.4f} segundos")
        print(f"Promedio de costo de la solicitud: ${promedio_costo:.6f} USD")
        print("------------------------------------------------------------")
except (ValueError, RuntimeError) as e:
    print(f"No se pudo completar la operación: {e}")