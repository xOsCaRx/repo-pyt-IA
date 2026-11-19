# IMPORTANTE: requiere rich para visualizar. Instalar con: pip3 install rich
# 2026-11-19 Creqción. Permite ver resultados de lo s registros de latencia y costo
import json
from pathlib import Path
from rich import print

ARCHIVO = "registros_latencia_costo.jsonl"

if not Path(ARCHIVO).is_file():
    print(f"[yellow]No existe {ARCHIVO}. Debes primero ejecutar registro_rag_core.py.[/yellow]")
else:
    registros = []
    costo_acumulado = 0.0
    registros_con_costo = 0

    with open(ARCHIVO, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            if linea.strip():
                registro = json.loads(linea)
                registros.append(registro)

                tokens = registro.get("tokens") or {}
                tiempos = registro.get("tiempos_ms", registro.get("tiempo_ms", {}))
                costo = registro.get("costo_estimado_generacion_usd")
                if costo is None:
                    costo = registro.get("costo_estimado_usd")

                if isinstance(costo, str):
                    try:
                        costo = float(costo.strip("[]"))
                    except ValueError:
                        costo = None

                if isinstance(costo, (int, float)):
                    costo_acumulado += costo
                    registros_con_costo += 1
                    costo_texto = f"USD {costo:.8f}"
                else:
                    costo_texto = "no disponible"

                print(
                    f"k={registro['k']}  "
                    f"entrada={tokens.get('input_tokens')} tokens  "
                    f"salida={tokens.get('output_tokens')} tokens  "
                    f"total={registro['tiempo_total_ms']} ms  "
                    f"generación={tiempos.get('generacion')} ms  "
                    f"costo={costo_texto}\n"
                    f"  Pregunta: {registro['pregunta']}"
                )

    print(f"Costo acumulado estimado de generación: USD {costo_acumulado:.8f}")