# 2026-11-03: Permite testear la cadena de cuatro pasos sin necesidad de conectarse a Gemini, utilizando un modelo falso (MagicMock) para simular las respuestas del modelo.
# 2026-11-03: Fecha creación

from unittest.mock import MagicMock
from langchain_core.messages import AIMessage

from tarea_cadena_pasos import construir_cadena

def test_cadena_conecta_los_cuatro_pasos():
    # Simulo cuatro respuestas consecutivas de Gemini
    modelo_falso = MagicMock()

    modelo_falso.side_effect = [
        AIMessage(content="Avance real 60%, planificado 80%."),
        AIMessage(content="Riesgo de incumplimiento del plazo."),
        AIMessage(content="Priorizar funcionalidades críticas."),
        AIMessage(content="Informe ejecutivo: proyecto con retraso y acciones de mitigación."),
    ]
    # Construyo la cadena utilizando el modelo falso
    cadena = construir_cadena(modelo_falso)

    # Ejecuto la cadena 
    resultado = cadena.invoke({
        "texto": "Proyecto con 60% de avance real y 80% planificado."
    })

    # Compruebo que el modelo fue llamado cuatro veces
    assert modelo_falso.call_count == 4

    # Compruebo que recibo el informe final
    assert "Informe ejecutivo" in resultado
