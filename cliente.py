# Script que permite reintentar la petición a una API 
# Fecha Creación: 2026-10-23

import time
from typing import Callable, Any 

from src.consumir_gemini import armar_peticion, enviar_peticion, extraer_texto, parsear_respuesta_json

def con_reintento(
    funcion: Callable[[], Any],
    intentos: int = 3,
    espera_segundos: int = 2
) -> Any:
    for intento in range(intentos):
        try:
            return funcion()
        except TimeoutError:
            if intento == intentos - 1:
                raise
            print(f"Intento {intento+1} de {intentos} falló por límite de uso/servidor. Reintentando...")
            time.sleep(espera_segundos)