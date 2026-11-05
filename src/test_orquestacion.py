from unittest.mock import MagicMock
from langchain_core.runnables import RunnableLambda

from enrutamiento_core import (
    construir_cadena_con_enrutamiento,
    construir_cadena_segura,
    procesar_consulta_segura,
)

def test_cadena_usa_fallback_ante_fallo():
    def fallar_a_proposito(datos):
        raise ConnectionError("Error de conexión simulado")

    cadena_falsa = RunnableLambda(fallar_a_proposito)
    cadena_segura = construir_cadena_segura(cadena_falsa)

    resultado = cadena_segura.invoke({"mensaje": "Identifica los riesgos"})

    assert "No fue posible analizar" in resultado


def test_procesar_consulta_segura_no_propaga_excepciones():
    clasificacion_falsa = MagicMock()
    clasificacion_falsa.side_effect = ConnectionError("Error simulado")

    cadena_falsa = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificacion_falsa,
        cadena_riesgos=RunnableLambda(lambda datos: "riesgos"),
        cadena_decisiones=RunnableLambda(lambda datos: "decisiones"),
        cadena_recuperacion=RunnableLambda(lambda datos: "recuperacion"),
    )

    resultado = procesar_consulta_segura(cadena_falsa, "Consulta de prueba")

    assert "No fue posible analizar" in resultado
    assert clasificacion_falsa.call_count == 1


def test_enrutamiento_envia_consulta_a_riesgos():
    clasificacion_falsa = RunnableLambda(lambda datos: "RIESGOS")
    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificacion_falsa,
        cadena_riesgos=RunnableLambda(lambda datos: "Riesgos identificados"),
        cadena_decisiones=RunnableLambda(lambda datos: "Decisiones evaluadas"),
        cadena_recuperacion=RunnableLambda(lambda datos: "Plan de recuperación"),
    )

    resultado = cadena.invoke({"mensaje": "¿Qué riesgos tiene mi proyecto?"})

    assert resultado == "Riesgos identificados"
