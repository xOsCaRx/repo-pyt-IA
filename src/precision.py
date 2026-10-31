# Fecha creación: 2026-10-30

from collections import Counter
from cliente import consultar_modelo
from pipeline_limpieza import procesar_texto
import json

# Casos con preguntas y referencias
casos = [
    # Avance, hitos y cronograma (1-5)
    (
        "Un proyecto debía llevar 80% de avance y lleva 60%. ¿Cuál es la desviación en puntos porcentuales?",
        "El proyecto presenta una desviación negativa de 20 puntos porcentuales respecto al avance planificado.",
    ),
    (
        "Un proyecto tiene cuatro semanas restantes y tres funcionalidades críticas sin terminar. ¿Qué riesgo debes destacar?",
        "Existe riesgo de incumplir la fecha de entrega por las tres funcionalidades críticas pendientes.",
    ),
    (
        "La integración con un proveedor está bloqueada desde hace dos semanas. ¿Qué efecto potencial tiene sobre el cronograma?",
        "El bloqueo de integración puede retrasar las actividades dependientes y comprometer el cronograma.",
    ),
    (
        "Un hito debía completarse el 10 de noviembre y se terminó el 15 de noviembre. ¿Cuál fue su retraso en días calendario?",
        "El hito terminó con cinco días calendario de retraso.",
    ),
    (
        "Un equipo completó 7 de 10 entregables comprometidos. ¿Qué porcentaje de entregables completó?",
        "El equipo completó el 70 por ciento de los entregables comprometidos.",
    ),
    # Presupuesto y recursos (6-10)
    (
        "El presupuesto total de un proyecto es de 20 millones de pesos y se han gastado 16 millones. ¿Qué porcentaje del presupuesto se consumió?",
        "Se consumió el 80 por ciento del presupuesto total del proyecto.",
    ),
    (
        "Un proyecto consumió 85% del presupuesto y completó 55% del trabajo. ¿Qué alerta de gestión corresponde emitir?",
        "Existe una alerta de posible sobrecosto porque el consumo presupuestario supera ampliamente el avance del trabajo.",
    ),
    (
        "Dos desarrolladores de un equipo de seis estarán ausentes durante dos semanas. ¿Qué riesgo operativo debes registrar?",
        "La ausencia temporal de dos desarrolladores reduce la capacidad del equipo y puede retrasar las entregas.",
    ),
    (
        "Un proyecto dispone de 5 millones de pesos adicionales y contratar apoyo cuesta 7 millones. ¿Es viable esa contratación con el presupuesto adicional disponible?",
        "La contratación no es viable con el presupuesto adicional disponible porque faltan dos millones de pesos.",
    ),
    (
        "El único especialista en una integración crítica estará ausente una semana. ¿Qué riesgo se identifica?",
        "Existe una dependencia de una persona clave que puede bloquear la integración crítica durante su ausencia.",
    ),
    # Riesgos, evidencias y priorización (11-15)
    (
        "Un proveedor informó que su entrega crítica se atrasará diez días. ¿Qué riesgo para el proyecto debes registrar?",
        "El atraso del proveedor puede postergar las tareas dependientes y afectar la fecha de entrega del proyecto.",
    ),
    (
        "Un riesgo tiene impacto alto y probabilidad alta. ¿Qué prioridad cualitativa debería asignarse para su tratamiento?",
        "El riesgo debe recibir prioridad alta y requiere un plan de respuesta oportuno.",
    ),
    (
        "Solo sabes que el avance es 50%, pero no tienes el avance planificado. ¿Puedes concluir que el proyecto está atrasado?",
        "No es posible determinar si hay retraso sin conocer el avance planificado para la misma fecha.",
    ),
    (
        "El gerente afirma que el proyecto terminará tarde, pero no aporta fechas ni avance planificado. ¿Debe registrarse como hecho verificado?",
        "La afirmación no debe registrarse como hecho verificado sin evidencia de fechas o avance planificado.",
    ),
    (
        "Una API externa falla de forma intermitente y bloquea pruebas de integración. ¿Qué acción preventiva conviene priorizar?",
        "Conviene coordinar con el proveedor la resolución de fallas y un plan de contingencia para las pruebas.",
    ),
    # Decisiones, recuperación y seguimiento (16-20)
    (
        "Quedan cuatro semanas y el alcance incluye tareas no esenciales. ¿Qué alternativa podría evaluarse para proteger la fecha de entrega?",
        "Se puede evaluar reducir el alcance no esencial y priorizar las funcionalidades críticas para proteger la fecha.",
    ),
    (
        "Un proyecto acumula retrasos y varias tareas dependen de una integración bloqueada. ¿Qué debe revisarse primero para planificar su recuperación?",
        "Debe revisarse la dependencia bloqueada y su efecto en la ruta crítica antes de definir la recuperación.",
    ),
    (
        "Un proyecto está retrasado y no se conoce la capacidad restante del equipo. ¿Qué dato falta para evaluar si puede recuperarse el plazo?",
        "Falta conocer la capacidad disponible del equipo y el esfuerzo pendiente para evaluar la recuperación del plazo.",
    ),
    (
        "Después de acordar un plan de recuperación, ¿qué indicador permite seguir si el avance real se acerca al planificado?",
        "La desviación entre el avance real y el avance planificado permite monitorear la recuperación del cronograma.",
    ),
    (
        "Un proyecto tiene riesgo de retraso y sobrecosto. ¿Qué debería incluir una recomendación ejecutiva útil?",
        "Una recomendación ejecutiva debe proponer una acción concreta, justificarla con evidencia e indicar su impacto esperado.",
    ),
]


# Cuenta las coincidencias entre referencia y respuesta.
def contar_coincidencias(tokens_referencia: list[str], tokens_respuesta: list[str]) -> int:
    conteo_referencia = Counter(tokens_referencia)
    conteo_respuesta = Counter(tokens_respuesta)
    interseccion = conteo_referencia & conteo_respuesta
    return sum(interseccion.values())


# Calcula precisión, cobertura y F1 de dos listas de tokens.
def calcular_precision_cobertura_f1(tokens_referencia: list[str], tokens_respuesta: list[str]) -> dict[str, float]:
    coincidencias = contar_coincidencias(tokens_referencia, tokens_respuesta)
    if not tokens_respuesta or not tokens_referencia:
        return {"precision": 0.0, "cobertura": 0.0, "f1": 0.0}
    precision = coincidencias / len(tokens_respuesta)
    cobertura = coincidencias / len(tokens_referencia)
    if precision + cobertura == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * cobertura / (precision + cobertura)
    resultado = {"precision": precision, "cobertura": cobertura, "f1": f1}
    return resultado


def calcular_metricas(texto_referencia, texto_respuesta):
    tokens_referencia = procesar_texto(texto_referencia)
    tokens_respuesta = procesar_texto(texto_respuesta)
    return calcular_precision_cobertura_f1(tokens_referencia, tokens_respuesta)


def resumir_metricas(resultados):
    if not resultados:
        return {"precision_promedio": 0, "cobertura_promedio": 0, "f1_promedio": 0}
    n = len(resultados)
    return {
        "precision_promedio": sum(r["precision"] for r in resultados) / n,
        "cobertura_promedio": sum(r["cobertura"] for r in resultados) / n,
        "f1_promedio": sum(r["f1"] for r in resultados) / n,
    }

def main():
    resultados = []
    for numero, (consulta, referencia) in enumerate(casos, 1):
        print(f"Consultando {numero}/{len(casos)}: {consulta}")
        try:
            respuesta = consultar_modelo(consulta)[0]  
            metricas = calcular_metricas(referencia, respuesta)
        except (TimeoutError, RuntimeError, ValueError, TypeError) as error:
            print(f"No se pudo completar la consulta {numero}: {error}")
            break

        resultados.append({
            "consulta": consulta,
            "referencia": referencia,  # Necesaria para la revisión manual
            "respuesta": respuesta,
            **metricas,
        })

        # Guardo cada iteración para conservar resultados ante fallos de API.
        with open("src/resultados_metricas.json", "w", encoding="utf-8") as archivo:
            json.dump(resultados, archivo, indent=2, ensure_ascii=False)

    peores_casos = sorted(resultados, key=lambda r: r["f1"])
    for caso in peores_casos[:3]:
        print(caso["consulta"], caso["f1"])
    print(f"Respuestas obtenidas: {len(resultados)}/20")


if __name__ == "__main__":
    main()