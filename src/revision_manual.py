# Fecha creación: 2026-10-30
# Permite abrir los resultados obtenidos, seleccionar 5 de f1 más bajos y f1 más altos y luego itero por cada uno para agregar evaluación

import json

# Abro los resultados
with open("resultados_metricas.json", "r", encoding="utf-8") as archivo:
    resultados = json.load(archivo)

peores_casos = sorted(resultados, key=lambda r: r["f1"])
muestra_para_revisar = peores_casos[:5] + peores_casos[-5:] # Solo tomo 10 casos 
revision_manual = []

for numero, caso in enumerate(muestra_para_revisar, 1):
    print(f"\nCaso {numero}/10 | F1: {caso['f1']:.3f}")
    print("Consulta:", caso["consulta"])
    print("Referencia:", caso["referencia"])
    print("Respuesta:", caso["respuesta"])

    #Reviso las respuestas en base a los criterios solicitados.
    correccion = input("Corrección factual [si/no/parcial]: ").strip().lower()
    completitud = input("Completitud [si/no/parcial]: ").strip().lower()
    contradiccion = input("¿Hay contradicción? [si/no]: ").strip().lower()
    nota = input("Explica la evaluación: ").strip()

    revision_manual.append({
        "consulta": caso["consulta"],
        "referencia": caso["referencia"],
        "respuesta": caso["respuesta"],
        "precision": caso["precision"],
        "cobertura": caso["cobertura"],
        "f1": caso["f1"],
        "correccion_factual": correccion,
        "completitud": completitud,
        "contradiccion": contradiccion,
        "nota": nota,
        "estado_revision": "revision_manual_realizada",
    })

    # Guardo tras cada caso para no perder revisiones por si se interrumpe.
    with open("src/revision_manual.json", "w", encoding="utf-8") as archivo:
        json.dump(revision_manual, archivo, indent=2, ensure_ascii=False)

print("\nFinalizado")