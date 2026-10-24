# CONSISTENCIA.PY : Script que permite ejecutar el banco de prompts y dejar el resultado dentro de registro_resultados.json
# Fecha creación: 2016-10-22
import json
import time
from prompt.banco import BANCO_DE_PROMPT
from consumir_gemini import armar_peticion, enviar_peticion, extraer_texto, parsear_respuesta_json
registro = {}

try:
    print("="*30)
    print("Iniciando verificación...")
    print("="*30)
    for prompt in BANCO_DE_PROMPT:
        exitos = 0
        intentos = 3
        for intento in range(intentos):
            url, body = armar_peticion("gemini-3.5-flash-lite", prompt["ejemplo_usuario"], prompt["system_instruction"], prompt["response_schema"])
            datos = enviar_peticion(url, body)
            respuesta_costo = extraer_texto(datos)
            claves_requeridas = prompt["claves_esperadas"]
            try:
                respuesta_formateada = (parsear_respuesta_json(respuesta_costo[0], claves_requeridas),) + respuesta_costo[1:]
                #print(f"Respuesta: {respuesta_formateada}")
                exitos += 1
            except ValueError as e:
                print(f"Intento {intento + 1} falló: {e}")
            time.sleep(1)
        print(f"{prompt["nombre"]}: {exitos} ({intentos} respuestas válidas)")
        registro[prompt["nombre"]] = {"exitos": exitos, "intentos": intentos}
    #Me permite vaciar el resultado dentro del archivo registro_resultados
    with open("src/registro_resultados.json", "w", encoding="utf-8") as archivo:
        json.dump(registro, archivo, indent=2, ensure_ascii=False)
    print("="*30)
    print("Verificación finalizada")
    print("="*30)
except(ValueError, RuntimeError) as e:
    print("No se pudo completar la operación: ", e)