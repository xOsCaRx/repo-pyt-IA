# Decisión de arquitectura: elección de modelo

**Fecha de comparación:** 21 de octubre de 2026  
**Nombre de la miniaplicación:** Asistente de IA para apoyo a la toma de decisiones en gestión de proyectos.

## Modelo elegido

Selecciono **Gemini 3.5 Flash Lite** para la primera versión de la miniaplicación.

La aplicación tiene como finalidad **apoyar a Project Managers, PMO, gerentes y líderes técnicos en la toma de decisiones sobre proyectos de software**. Debe analizar el estado y avance, los riesgos y bloqueos, los recursos y presupuesto, y los indicadores de desempeño. A partir de esta información, propondrá **recomendaciones de acción justificadas**. Se contempla incorporar progresivamente datos de archivos, APIs y bases de datos.

Los requisitos que necesito cumplir son:

- **R1 - Análisis contextual:** interpretar datos sobre avance, presupuesto, recursos y riesgos de un proyecto.
- **R2 - Identificación de problemas:** reconocer desviaciones, bloqueos y riesgos prioritarios.
- **R3 - Recomendaciones accionables:** proponer medidas correctivas ordenadas por prioridad y explicar su efecto previsto en plazo, costo y alcance.
- **R4 - Fundamentación verificable:** distinguir hechos de inferencias, no inventar información e identificar los datos faltantes para tomar una decisión.
- **R5 - Eficiencia operativa:** mantener un costo por consulta conveniente y una latencia razonable para un asistente de este tipo.
- **R6 - Evolución incremental:** aprovechar el componente inicial para incorporar orquestación, RAG y una API propia en etapas posteriores.
  
## Diagrama de arquitectura

[Diagrama de arquitectura] - (./docs/diagrama.excalidraw.png)

## Comparación de candidatos
Los tres modelos recibieron **el mismo prompt de evaluación**, y se realizaron cuatro request por modelo. El prompt describía un proyecto de software con 70 % de avance planificado, 55 % de avance real, 80 % del presupuesto consumido, seis semanas restantes y dos desarrolladores clave ausentes durante dos semanas. Se les pidió identificar tres riesgos, recomendar tres acciones ordenadas por prioridad, explicar impactos en plazo/costo/alcance, separar hechos de inferencias y declarar qué información adicional necesitaban. 

**El prompt enviado es el siguiente:** 
"Actúa como un asesor experto en gestión de proyectos de software. Un proyecto tiene un avance planificado del 70%, pero su avance real es del 55%. Se ha consumido el 80% del presupuesto, quedan 6 semanas para la fecha de entrega y dos desarrolladores clave estarán ausentes durante las próximas 2 semanas. Analiza la situación e identifica los tres riesgos más importantes. Propón tres acciones correctivas, ordénalas por prioridad y explica el impacto esperado de cada una sobre el plazo, costo y alcance. Separa los hechos de tus inferencias y señala qué información adicional necesitas para fundamentar mejor las recomendaciones. No inventes datos."

Los modelos fueron comparados mediante criterios vinculados al propósito de la aplicación:

1. **Calidad de la respuesta y utilidad para la decisión:** comprensión del escenario, identificación de riesgos, relevancia y priorización de acciones, y justificación de sus impactos.
2. **Confiabilidad del razonamiento:** corrección de los cálculos, diferenciación entre hechos e inferencias, reconocimiento de información faltante y ausencia de afirmaciones no sustentadas.
3. **Costo de operación:** tarifas de entrada y salida por token y costo promedio reportado de cuatro solicitudes.
4. **Latencia:** tiempo promedio medido por solicitud.

### Tabla comparativa

| Indicador | Gemini 3.5 Flash Lite | Gemini 3.6 Flash | Gemini 3.8 Flash |
|---|---:|---:|---:|
| Costo de entrada por token (USD) | 0,00000030 | 0,00000075 | 0,00000075 |
| Costo de salida por token (USD) | 0,00000250 | 0,00000150 | 0,00000375 |
| Costo promedio de 4 solicitudes (USD) | **0,003628** | 0,004300 | 0,009975 |
| Latencia promedio de 4 solicitudes (segundos) | **6,6958** | 18,4093 | 49,83975 |
| Identificación de riesgos | Pertinente | Pertinente | Pertinente |
| Recomendaciones | Claras y aplicables | Más estructuradas metodológicamente | Detalladas y con mayor énfasis cuantitativo |
| Fundamentación cuantitativa | Básica | Intermedia | Más desarrollada |
| Limitación observada | Conclusión demasiado categórica sobre imposibilidad presupuestaria | Da por ciertos efectos sobre ruta crítica y cumplimiento | Probabilidad de incumplimiento casi del 100 % sin base suficiente y otras garantías injustificadas |

**IMPORTANTE**: *Las mediciones de costo y latencia son las obtenidas en las pruebas.
Las valoraciones de calidad son cualitativas, obtenidas del análisis de las tres respuestas.*

## Justificación

Elijo **Gemini 3.5 Flash Lite** porque en el escenario evaluado, pudo responder de acuerdo a las necesidades funcionales centrales de la miniaplicación: identificó el desfase entre el avance planificado y real, detectó riesgos de plazo, presupuesto y calidad, y propuso acciones concretas y priorizadas para abordar esas dificultades. También distinguió hechos e inferencias y solicitó información faltante antes de afinar las recomendaciones.

Por otro lado, los resultados observados cumplen de forma preliminar con los primeros 4 requisitos. Además, el menor costo promedio reportado (**USD 0,003628**) y la menor latencia (**6,6958 segundos**) favorecen el requisito 5. En la muestra evaludada, Gemini 3.6 Flash costó **18,52 % más** y tardó **174,94 % más**, mientras que Gemini 3.8 Flash costó **174,94 % más** y tardó **644,34 % más**, en comparación con el modelo seleccionado.

Es **importante** mencionar que la selección corresponde a una **primera miniaplicación y a esta prueba específica**. No significa que Gemini 3.5 Flash Lite sea superior en cualquier tarea o volumen de uso. Su propia respuesta contiene una inferencia demasiado fuerte: calificar como matemáticamente imposible la finalización del alcance con el presupuesto restante sin conocer todas las condiciones del proyecto. Considero que antes de usar recomendaciones para decisiones reales será necesario validar cálculos, reforzar instrucciones de incertidumbre y ampliar los escenarios de prueba.

**Datos utilizados** 

La conclusión se apoya únicamente en: 

a) Las respuestas proporcionadas por los modelos bajo el mismo escenario y 

b) Los valores obtenidos de las tarifas por token, costo promedio para cuatro solicitudes y latencia promedio. 

## Alternativa descartada y por qué

### Gemini 3.6 Flash

**No se selecciona** porque aunque ofrece una estructura metodológica más explícita (por ejemplo, priorización MoSCoW y reestimación del proyecto), en la respuesta observada no demuestra una mejora decisiva de las recomendaciones respecto del modelo elegido. Además, presenta afirmaciones no verificadas sobre la ruta crítica y las posibilidades de cumplir el plazo. Su costo promedio fue **18,52 % superior** y su latencia **174,94 % superior** a la de Gemini 3.5 Flash Lite. Es una alternativa a reconsiderar si futuras pruebas muestran una ventaja de calidad consistente.

### Gemini 3.8 Flash

**No se selecciona** porque su mayor desarrollo cuantitativo no compensó el costo ni la espera observados. El costo promedio fue **174,94 % superior** y la latencia **644,34 % superior** a la del modelo elegido. Además, introdujo una afirmación de probabilidad de incumplimiento «casi del 100 %» sin datos ni método suficiente para sustentarla, lo que es especialmente problemático para una aplicación que apoya decisiones.

