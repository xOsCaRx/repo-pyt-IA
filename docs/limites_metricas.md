# Límites de la métrica de evaluación

## Qué mide

Precisión, cobertura y F1 comparan las palabras de la respuesta de Gemini con una referencia, considerando sus repeticiones. **No miden si la respuesta es correcta.**
En resumen: 
- **Precisión**: cuánto del texto generado coincide con la referencia.
- **Cobertura**: cuánto de la referencia aparece en el texto generado.
- **F1**: una combinación de las dos anteriores.

## Modos de falla conocidos

- **Respuestas extensas:** ante un riesgo de retraso, Gemini identificó el problema, pero agregó tantas explicaciones que obtuvo un F1 de **0,06**.
- **Errores que F1 no detecta bien:** ante la ausencia de 2 de 6 desarrolladores, calculó correctamente una reducción del **33 %**, pero también afirmó que quedaría solo un tercio de la capacidad cuando en realidad quedarían dos tercios.
- **Redacción distinta:** una respuesta puede proponer una acción adecuada usando palabras diferentes de la referencia y recibir un F1 bajo.

## Muestra revisada

Se generaron **20 respuestas** sobre gestión de proyectos (**resultados_metricas.json**). Se seleccionaron **10 casos** para evaluación cualitativa: los **5 F1 más bajos** y los **5 más altos**, considerando corrección factual, completitud y contradicciones. En el archivo **revision_manual.json** se puede revisar en detalle la evaluación cualitativa.

## Recomendación de uso

Usaría F1 para **detectar respuestas que conviene revisar**, no para aprobarlas automáticamente. Verificaría manualmente cifras, supuestos y recomendaciones antes de utilizarlas para tomar decisiones en un proyecto.
