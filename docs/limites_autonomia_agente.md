# Límites de autonomía: agente de apoyo a la gestión de proyectos

## Herramientas y nivel de riesgo

| Herramienta | Categoría | Riesgo | Justificación |
|---|---|---|---|
| `consultar_estado_proyecto` | Solo lectura | Bajo | Consulta avance, estado y riesgos. No modifica información. |
| `calcular_costo_actividad` | Solo lectura / cálculo | Bajo | Calcula una estimación con los valores entregados. No registra compromisos ni mueve fondos. |
| `actualizar_estado_tarea` | Escritura reversible | Medio | Modifica un estado dentro del diccionario de prueba. Si se registra un estado equivocado puede corregirse asignando el estado anterior. |
| `registrar_gasto_proyecto` | Escritura de impacto económico | Alto | Descuenta un monto del presupuesto. Si esta acción se conectara a un sistema real, podría comprometer recursos. Por eso exige aprobación humana previa. |

## Herramientas que requieren aprobación humana

- **`registrar_gasto_proyecto`: sí requiere aprobación.** Antes de descontar fondos valida el proyecto, monto positivo y presupuesto disponible. Luego llama a `esperar_aprobacion(...)`. Solo la respuesta `s` dentro del plazo autoriza el gasto, `n`, falta de respuesta o tiempo agotado lo rechazan. La decisión se guarda en `aprobaciones_agente.jsonl`.
- **`actualizar_estado_tarea`: no requiere aprobación previa.** Es reversible y alamacenamos su traza.
- **`consultar_estado_proyecto` y `calcular_costo_actividad`: no requieren aprobación.** Son operaciones de lectura o cálculo, sin efecto sobre el estado del proyecto.

## Revisión de trazas

- **Archivo:** `trazas_agente.jsonl` registra fecha, sesión, entrada, herramientas utilizadas, argumentos, observaciones y respuesta final. `aprobaciones_agente.jsonl` registra cada decisión de aprobación. Ambos se crean al ejecutar las acciones correspondientes.
- **Frecuencia para esta actividad:** revisar **cada ejecución de prueba** y verificar al menos una interacción de riesgo bajo, medio y alto. Para una prueba piloto posterior, revisar **diariamente** las acciones de riesgo alto y **semanalmente** una muestra de las demás. Son frecuencias propuestas, no un control automático del código.
- **Patrones sospechosos:** uso de herramientas no pertinentes para la pregunta; llamadas repetidas innecesariamente; argumentos incorrectos o inventados; cambios de estado no solicitados; gastos sin intención explícita del usuario; discrepancias entre herramientas utilizadas y respuesta final; intentos de gasto rechazados o solicitudes de gasto reiteradas.
- **Revisión adicional del riesgo alto:** comparar cada registro de `registrar_gasto_proyecto` con `aprobaciones_agente.jsonl`, corroborando el monto, proyecto, decisión y que los gastos rechazados no se ejecutaron. Los archivos actuales no incluyen un identificador único común por operación: la correlación precisa necesitaría mejorarse antes de uso real.

## Qué hacer ante un comportamiento inesperado

1. **Contener:** detener el script.
2. **Revisar las evidencias:** abrir la línea afectada de `trazas_agente.jsonl` y, si corresponde, la aprobación registrada en `aprobaciones_agente.jsonl`.
3. **Identificar la causa:** comparar la solicitud del usuario, los argumentos seleccionados por el agente, la observación de la herramienta y la respuesta final. Confirmar si hay datos incorrectos, una descripción ambigua de `@tool` o instrucciones insuficientes del prompt.
4. **Corregir el comportamiento:** ajustar la descripción de la herramienta, las validaciones o las instrucciones del sistema. No eliminar la aprobación humana como forma de solucionar un bloqueo.
5. **Volver a probar:** repetir el caso que falló, junto con una consulta de bajo riesgo y un gasto rechazado. Comprobar nuevamente la traza y el registro de aprobaciones.
6. **Reactivar de manera controlada:** si se desactivó una tool, reactivarla solo cuando las pruebas muestren el comportamiento esperado.