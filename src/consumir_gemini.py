import os
import requests
from dotenv import load_dotenv
import time # Para contabulizar el tiempo
import json
import re

#----------------------------------------------------------------------------------------------------
# Función que permite cargar secretos y configuraciones desde .env
#----------------------------------------------------------------------------------------------------
load_dotenv()

#----------------------------------------------------------------------------------------------------
#region Constantes
# Fecha de actualización: 2026-10-19
#----------------------------------------------------------------------------------------------------
GEMINI_URL_BASE = f"https://generativelanguage.googleapis.com/v1beta/models/"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SYSTEM_INSTRUCTION = "Actúa como un asesor experto en gestión de proyectos de software. Responde de manera ejecutiva y profesional sin inventar datos y solo basándote en la información entregada"
#endregion
#----------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------
#region Variables globales
# Fecha de actualización: 2026-10-19
#----------------------------------------------------------------------------------------------------
gemini_model = "gemini-flash-latest"
gemini_precio_entrada = 0
gemini_precio_salida = 0
valor_dolar_chile = 970
#endregion
#----------------------------------------------------------------------------------------------------

# Crear solicitud
# 2026-10-22: Se incorpora como parámetro gemini_model_seleccionado para poder utilizarlo en consistencia.py
# 2026-10-21: Se agrega system instruction y response_schema al body del request 
# 2026-10-20: Se agrega un response_schema para recibir mi respuesta formateada y manejable
#----------------------------------------------------------------------------------------------------
def armar_peticion(gemini_model_seleccionado, pregunta, system_instruction, response_schema=None):
    if not pregunta: raise ValueError("La pregunta no puede estar vacía.")
    url = f"{GEMINI_URL_BASE}{gemini_model_seleccionado}:generateContent?key={GEMINI_API_KEY}"
    body = { 
        "systemInstruction": { "parts": [{ "text": system_instruction }] }, 
        "contents": [{ "parts": [{ "text": pregunta }] }]
        }
    if response_schema is not None: # Si efectivamente recibo un schema entonces lo agrego
        body["generationConfig"] = {
            "responseMimeType" : "application/json",
            "responseSchema"   : response_schema
        }
    return url, body

#----------------------------------------------------------------------------------------------------
# Enviar petición
#----------------------------------------------------------------------------------------------------
def enviar_peticion(url, body):
    try:
        response = requests.post(url, json=body, timeout=30)
        #raise TimeoutError()
    except requests.exceptions.ConnectionError:
        raise RuntimeError("No se pudo conectar con el servicio. Itente nuevamente más tarde.")
    except requests.exceptions.Timeout:
        raise RuntimeError("La solicitud ha excedido el tiempo de espera. Intente nuevamente más tarde.")

    if response.status_code in (401,403):
        raise ValueError("Credencial inválida o sin permiso. Revisa tu GEMINI_API_KEY")

    if response.status_code >= 500:
        raise TimeoutError("El proveedor no pudo procesar la petición. Espere un momento y reintente nuevamente")

    if response.status_code == 429:
        segundos = response.headers.get("Retry-After")
        mensaje = f"Límite excedido. Reintentar en {segundos}s." if segundos else "Límite excedido."
        raise TimeoutError(mensaje)

    if response.status_code != 200:
        raise RuntimeError(f"Error en la solicitud: {response.status_code} - {response.text}")
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        raise RuntimeError("La respuesta del servicio no llegó en el formato esperado.")

#----------------------------------------------------------------------------------------------------
# Extraer texto: Permite extraer el texto de la respuesta de la API y calcular el costo de la misma.
# Última modificación: 2026-10-19
#----------------------------------------------------------------------------------------------------
def extraer_texto(datos):
    try:
        costo = calcular_costo(datos, precio_entrada=gemini_precio_entrada, precio_salida=gemini_precio_salida)
        return datos["candidates"][0]["content"]["parts"][0]["text"], costo
    except (KeyError, IndexError, TypeError):
        raise RuntimeError("Error al extraer el texto de la respuesta.")    

#----------------------------------------------------------------------------------------------------
# Crear Schema: Crea el esquema del response
# Fecha de creación: 2026-10-21
#----------------------------------------------------------------------------------------------------
def crear_schema():
    response_schema = {
        "type": "OBJECT",
        "properties": {
            "estado_analisis": {
                "type": "STRING",
                "enum": ["completo", "parcial", "datos_insuficientes"],
                "description": "Determina si hay información suficiente para emitir recomendaciones."
            },
            "resumen_ejecutivo": {
                "type": "STRING",
                "description": "Diagnóstico ejecutivo del estado general del proyecto."
            },
            "hechos": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "descripcion": {"type": "STRING"},
                        "evidencia": {"type": "STRING"}
                    }
                    #,
                    #"required": ["descripcion", "evidencia"]
                },
                "description": "Hechos verificables extraídos de los datos proporcionados."
            },
            "inferencias": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "descripcion": {"type": "STRING"},
                        "fundamento": {"type": "STRING"}
                    }
                    #,
                    #"required": ["descripcion", "fundamento"]
                }
            },
            "riesgos": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "id": {"type": "STRING"},
                        "descripcion": {"type": "STRING"},
                        "prioridad": {
                            "type": "STRING",
                            "enum": ["alta", "media", "baja"]
                        },
                        "impacto": {"type": "STRING"},
                        "evidencia": {"type": "STRING"}
                    }
                    #,
                    #"required": [
                    #    "id", "descripcion", "prioridad",
                    #    "impacto", "evidencia"
                    #]
                }
            },
            "recomendaciones": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "prioridad": {
                            "type": "INTEGER",
                            "minimum": 1,
                            "maximum": 3
                        },
                        "accion": {"type": "STRING"},
                        "justificacion": {"type": "STRING"},
                        "impacto_esperado": {"type": "STRING"},
                        "riesgo_asociado": {"type": "STRING"}
                    }
                    #,
                    #"required": [
                    #    "prioridad", "accion", "justificacion",
                    #    "impacto_esperado", "riesgo_asociado"
                    #]
                }
            },
            "datos_faltantes": {
                "type": "ARRAY",
                "items": {"type": "STRING"}
            },
            "advertencias": {
                "type": "ARRAY",
                "items": {"type": "STRING"}
            }
        },
        "required": [
            "estado_analisis",
            "resumen_ejecutivo",
            "hechos",
            "inferencias",
            "riesgos",
            "recomendaciones",
            "datos_faltantes",
            "advertencias"
        ]
    }
    return response_schema

#----------------------------------------------------------------------------------------------------
# Obtener respuesta: Permite obtener la respuesta de la API 
# 2026-10-21 : Se agrega system instruction al body del request 
# 2026-10-20 : Se agregó la medición de latencia para evaluar el tiempo de respuesta de la API.
#----------------------------------------------------------------------------------------------------
def obtener_respuesta(pregunta):
    response_schema = crear_schema()
    url, body = armar_peticion(gemini_model, pregunta, SYSTEM_INSTRUCTION, response_schema)
    inicio_rqst = time.perf_counter() # Inicia el contador de tiempo
    datos = enviar_peticion(url, body)
    fin_rqst = time.perf_counter() # Finaliza el contador de tiempo
    latencia = fin_rqst - inicio_rqst
    respuesta_costo = extraer_texto(datos)
    claves_requeridas= ["estado_analisis","resumen_ejecutivo","hechos","inferencias",
                        "riesgos","recomendaciones","datos_faltantes","advertencias"
                        ]
    respuesta_formateada = (parsear_respuesta_json(respuesta_costo[0], claves_requeridas),) + respuesta_costo[1:]
    return respuesta_formateada, latencia

#----------------------------------------------------------------------------------------------------
# parsear_respuesta_json: Permite parsear la respuesta que recibo de la API
# Fecha creación: 2026-10-21
#----------------------------------------------------------------------------------------------------
def parsear_respuesta_json(response, claves_requeridas=None):
    clean_response = response.strip()
    clean_response = re.sub(r"^```(?:json)?\s*", "", clean_response) 
    clean_response = re.sub(r"\s*```$", "", clean_response)
    try:
        datos = json.loads(clean_response)
    except json.JSONDecodeError:
        raise ValueError("La respuesta del modelo JSON no es válida")
    if claves_requeridas:
        faltantes = [clave for clave in claves_requeridas if clave not in datos]
        if faltantes:
            raise ValueError("La respuesta no tiene la estructura esperada")
    return datos

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
# Muestra un menú para seleccionar el modelo
# Fecha creación : 2026-10-21
#----------------------------------------------------------------------------------------------------    
def mostrar_menu():
    os.system("clear")
    print("\n" + "=" * 30)
    print("MODELOS DISPONIBLES")
    print("=" * 30)
    print("  1. gemini-3.5-flash-lite")
    print("  2. gemini-3.6-flash")
    print("  3. gemini-3.8-flash")
    print("  4. Salir")
    print("=" * 30)

#----------------------------------------------------------------------------------------------------
# Asigno las variables de acuerdo al modelo seleccionado
# Fecha creación : 2026-10-21
#----------------------------------------------------------------------------------------------------
def seleccionar_modelo():
    global gemini_model, gemini_precio_entrada, gemini_precio_salida # Le indico que use las variables globales y no locales
    while True:
        mostrar_menu()
        opcion = input("Selecciona una opción: ").strip()

        match opcion:
            case "1":
                gemini_model = "gemini-3.5-flash-lite"
                gemini_precio_entrada = 0.0000003
                gemini_precio_salida = 0.0000025
                capturar_pregunta()
                break
            case "2":
                gemini_model = "gemini-3.6-flash"
                gemini_precio_entrada = 0.00000075
                gemini_precio_salida = 0.0000015
                capturar_pregunta()
                break
            case "3":
                gemini_model = "gemini-3.8-flash"
                gemini_precio_entrada = 0.00000075
                gemini_precio_salida = 0.00000375
                capturar_pregunta()
                break
            case "4":
                print("\n¡Saludos!")
                break
            case _:
                print("\nOpción inválida. Intenta nuevamente.")
                break;

#----------------------------------------------------------------------------------------------------
# Permite capturar la pregunta del usuario que haremos al modelo
# Fecha creación : 2026-10-21
#----------------------------------------------------------------------------------------------------
def capturar_pregunta():
    try:        
        (respuesta, costo), latencia = obtener_respuesta(input("Ingrese su pregunta: "))
        print("="*70)
        print(f"Respuesta: {respuesta}")
        print("="*70)
        print(f"Modelo: {gemini_model}")
        print(f"Costo estimado de la respuesta: ${costo:.6f} USD / ${costo * valor_dolar_chile:.2f} CLP")
        print(f"Latencia de la solicitud: {latencia:.4f} segundos")
        print("="*70)
    except (ValueError, RuntimeError) as e:
        print(f"No se pudo completar la operación: {e}")

#----------------------------------------------------------------------------------------------------
# Main: Inicio de la aplicación
# 2026-10-22 : Se agrega if que permite verificar que estamos ejecutando el script desde import o no
# 2026-10-21 : Se crea nueva función que muestra menú y según ello seleccionar modelo y continuar.
# 2026-10-20 : Se agregó la medición de latencia para evaluar el tiempo de respuesta de la API.
#----------------------------------------------------------------------------------------------------
if __name__ == "__main__" : #Esto permite que solo se ejecute cuando lo llamo desde este file de script y no desde un import
    seleccionar_modelo()

