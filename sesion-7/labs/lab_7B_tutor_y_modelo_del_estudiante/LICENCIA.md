# Laboratorio 7B: origen del modelo y de los datos

## Bayesian Knowledge Tracing

El modelo es de Corbett, A. T. y Anderson, J. R. (1994). Knowledge tracing: modeling the acquisition of procedural knowledge. *User Modeling and User-Adapted Interaction* 4(4), 253–278. El módulo `tutor.py` lo implementa en numpy desde sus ecuaciones, sin copiar código de otros proyectos.

Los topes de la adivinanza (0.3) y del descuido (0.1) vienen de Baker, R., Corbett, A. T. y Aleven, V. (2008). More accurate student modeling through contextual estimation of slip and guess probabilities. *ITS 2008*.

## Los técnicos

Todos los técnicos salen de una simulación con parámetros conocidos. No hay datos de personas reales. MantenIA es una empresa ficticia del curso, y sus parámetros son ilustrativos.

- Las secciones 2 a 4 y la 6.1 simulan con la semilla 7. Usan el mismo orden de sorteos de los ejemplos de las diapositivas, así que sus cifras coinciden.
- El contrapunto usa 10 técnicos simulados con la semilla 2026 (ver `datos/LEEME.md`).

## Las respuestas grabadas

`grabaciones/respuestas.json` guarda respuestas reales de Claude Haiku 5.5, de Anthropic. Las obtuvimos el 9 de noviembre de 2026, con los prompts del notebook.
