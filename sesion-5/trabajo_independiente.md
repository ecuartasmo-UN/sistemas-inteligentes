# Sesión 5 · Trabajo independiente

**Sistemas Inteligentes · Especialización en Inteligencia Artificial · UNAL Manizales**
Unidad 5: Redes Neuronales y Aprendizaje Profundo

| Trabajo | Charla | Tipo | Tiempo estimado | Entrega |
|---|---|---|---|---|
| TI-1 · Entrene una red sin escribir código | Inicial · De la neurona a la red profunda | Ejercicio individual | 65 min | Inicio de la semana 4 |
| TI-2 · Lleve el Laboratorio 5B a su organización | Intermedia · La arquitectura transformer | Ejercicio individual | 70 min | Inicio de la semana 4 |
| Paso del proyecto del curso | De cierre · De los transformers a los LLMs | En equipo | 60 min | La fecha se anuncia en clase |
| **Total** | | | **3 h 15 min** | |

**Sobre el tiempo.** Cada sesión del bloque presencial genera unas 12 horas de trabajo independiente (Anexo A del programa). Estos dos trabajos y el paso del proyecto ocupan 3 h 15 min. El resto se dedica a terminar los laboratorios 5A y 5B y a la lectura de la sesión 6.

**Ninguno pide programar.** Se hacen con herramientas en el navegador, una hoja de cálculo, un LLM y los notebooks de los laboratorios, cambiando datos y parámetros en sus celdas de configuración.

**Formato de entrega.** Un archivo PDF por trabajo, por el canal del curso. Los dos trabajos son individuales; el paso del proyecto es del equipo. Puede usar asistentes de IA generativa como herramienta de consulta, declarando cómo los usó; en el TI-2 el LLM es parte del ejercicio.

**Sin datos personales.** Los textos y datos de estos trabajos **no deben contener datos personales** (nombres, documentos, teléfonos, correos, direcciones) ni información confidencial de su organización. Si sus textos reales los tienen, reescríbalos con datos inventados antes de usarlos, y nunca los pegue tal cual en un LLM externo.

---

## TI-1 · Entrene una red sin escribir código

**Charla inicial · 65 minutos**

**Propósito.** Ver con sus propios ojos lo que vimos en la charla inicial y en el Laboratorio 5A: qué cambia al hacer una red más profunda o más ancha, qué hace la tasa de aprendizaje y cómo se ve el sobreajuste. Después, llevarlo a un problema de su organización.

**Instrucciones**

1. Abra [TensorFlow Playground](https://playground.tensorflow.org/) en el navegador. No hay que instalar nada. Permite hasta 6 capas ocultas de hasta 8 neuronas, y cambiar la activación, la tasa de aprendizaje, la regularización, el ruido y la proporción de datos de prueba.
2. **El límite de una línea.** Elija el conjunto de datos de cuadrantes (el «O exclusivo»). Quite todas las capas ocultas y entrene: ¿qué pasa? Agregue una capa oculta de 4 neuronas y entrene otra vez. Anote la pérdida de prueba (*test loss*) de cada caso.
3. **Profundidad y anchura.** Elija el conjunto en espiral. Pruebe al menos tres redes, por ejemplo 1 capa de 2 neuronas, 2 capas de 4 y 4 capas de 8. Entrene cada una unas 500 épocas y anote su pérdida de prueba.
4. **La tasa de aprendizaje.** Con la red que mejor le funcionó, pruebe tasas de 0,003, 0,03 y 3. Describa en una línea qué pasa con cada una, con las palabras de la charla: ¿llega al fondo del valle, rebota o no llega?
5. **El sobreajuste.** Suba el ruido a 40 o 50, baje los datos de entrenamiento al 10 % y use una red grande. Observe la pérdida de entrenamiento y la de prueba: ¿se separan? Luego active la regularización L2 con una tasa de 0,003 o 0,01 y compare.
6. **Su organización.** Elija un problema de clasificación de su organización, como aprobar o no una solicitud, predecir si un pedido llegará tarde o si un equipo fallará. Responda: ¿qué entradas tendría la red y qué salida?, ¿cuántos ejemplos etiquetados tiene o podría reunir?, ¿cómo separaría los datos para detectar el sobreajuste?
7. Responda en media página:
   - ¿Qué le enseñaron los experimentos sobre la profundidad, la tasa de aprendizaje y el sobreajuste?
   - Para el problema de su organización, ¿una red neuronal es una buena opción, o un modelo más simple? Use la guía de decisión de la charla de cierre.

**Entregable.** PDF de 1 a 2 páginas con la tabla de experimentos (configuración, épocas, pérdida de entrenamiento y de prueba), dos capturas de pantalla del Playground, las respuestas sobre su organización y la reflexión.

**Criterios de evaluación**

| Criterio | Peso |
|---|---|
| Experimentos completos y bien registrados | 40 % |
| Lectura correcta de las curvas: valle, tasa de aprendizaje y sobreajuste | 30 % |
| Conexión con un problema de su organización, sin datos personales | 30 % |

**Apoyo**
- La charla inicial de esta sesión, en particular «Aprender es bajar un valle con niebla» y «Memorizar no es aprender».
- Prince, S. J. D. (2023). [*Understanding Deep Learning*](https://udlbook.github.io/udlbook/), capítulos 3, 4 y 9 (redes superficiales, redes profundas y regularización). Libro gratuito, en inglés.
- Si quiere ir más allá con datos reales: el notebook del Laboratorio 5A, cambiando las capas, las neuronas y el dropout en su celda de configuración.

---

## TI-2 · Lleve el Laboratorio 5B a su organización

**Charla intermedia · 70 minutos**

**Propósito.** Comprobar con textos de su trabajo lo que gana un transformer preentrenado frente a las arquitecturas previas, dónde falla, y cuánto costaría hacerlo con un LLM.

**Instrucciones**

1. Elija un problema de su organización que consista en **clasificar textos cortos** en 3 o 4 clases. Por ejemplo: solicitudes según el área que las atiende, quejas según su tipo, correos según su prioridad, órdenes según el equipo.
2. Escriba de 30 a 60 textos de una o dos líneas, al menos 8 por clase, con su clase real. Si se basa en textos reales, **reescríbalos sin datos personales ni confidenciales**.
3. En el notebook del Laboratorio 5B, cargue sus textos en la sección para textos propios y compare las tres arquitecturas (bolsa de palabras, red recurrente y transformer preentrenado) con 3, 5 y 10 ejemplos por clase. Anote los aciertos de cada una.
4. Clasifique los mismos textos con un LLM (Claude, Gemini o ChatGPT), con una instrucción como esta:

   > Clasifica este texto en una de estas clases: [clase 1], [clase 2], [clase 3]. Responde solo con el nombre de la clase.

   Cuente sus aciertos.
5. Escriba tres textos difíciles: uno con sinónimos o jerga de su área, uno con una negación («no hay…», «ya no…») y uno ambiguo. ¿Qué arquitectura acierta en cada uno?
6. Estime el **costo** de clasificar 1000 textos con el LLM: cuente los tokens de la instrucción y de un texto típico, y use los precios oficiales. Compárelo con el transformer pequeño, que corre en su computador.
7. Responda en media página:
   - ¿Qué arquitectura acertó más, con cuántos ejemplos, y en qué falló cada una?
   - Con la guía de decisión de la charla de cierre: ¿qué usaría en su organización, considerando los ejemplos etiquetados, el costo, la privacidad de los textos y la explicabilidad?

**Entregable.** PDF de 1 a 2 páginas con las clases y una muestra de sus textos, la tabla de aciertos por arquitectura y número de ejemplos, el resultado del LLM, los tres textos difíciles, el cálculo de costo y la reflexión.

**Criterios de evaluación**

| Criterio | Peso |
|---|---|
| Conjunto de textos bien definido, sin datos personales | 25 % |
| Comparación de arquitecturas, LLM y costo hecha correctamente | 40 % |
| Análisis de errores y reflexión con los conceptos de la sesión: embeddings, atención, preentrenamiento y costo por token | 35 % |

**Para leer con criterio.** Sesenta textos no bastan para elegir un sistema de producción: sirven para entender cómo se equivoca cada arquitectura. Una decisión real exige muchos más ejemplos, tomados de la operación.

**Apoyo**
- Si quiere ver por dentro un transformer pequeño sin instalar nada: [Transformer Explainer](https://poloclub.github.io/transformer-explainer/), de Polo Club (Georgia Tech), licencia MIT. Corre GPT-2 en el navegador y muestra la atención y el efecto de la temperatura.
- Prince, S. J. D. (2023). [*Understanding Deep Learning*](https://udlbook.github.io/udlbook/), capítulo 12 (transformers).
- Precios oficiales para el cálculo de costo: [Anthropic](https://platform.claude.com/docs/en/about-claude/pricing), [OpenAI](https://developers.openai.com/api/docs/pricing) y [Google](https://ai.google.dev/gemini-api/docs/pricing).

---

## Paso del proyecto del curso

**Charla de cierre · en equipo · 60 minutos**

**Propósito.** Llevar la Unidad 5 al proyecto del equipo, que es libre y se construye con vibe coding: identificar si alguna parte la podría resolver una red neuronal o un LLM, con qué datos y cómo se verificaría.

**Instrucciones**

1. Revise el proyecto del equipo: ¿hay una parte que consista en **clasificar, predecir, leer texto o generar texto**?
2. Si la hay, agregue al plan.md un paso que describa ese componente: qué entra, qué sale y qué decisión apoya.
3. Agregue un paso para **elegir el tipo de modelo** con la guía de decisión de la charla de cierre (LLM vía API, modelo preentrenado pequeño, red propia o modelo clásico), y justifíquelo por los datos, los ejemplos etiquetados, el costo, la explicabilidad y la privacidad.
4. Agregue un paso sobre **los datos**: de dónde saldrán, cuántos ejemplos etiquetados hay y si contienen datos personales.
5. Agregue un paso sobre **la verificación**: cómo se comprobará el resultado del modelo (casos de prueba, una regla de negocio, una revisión humana). Es el patrón de toda la unidad: la red propone, otra técnica verifica.
6. Si el proyecto no necesita una red neuronal, explique en el plan.md por qué, en un párrafo.
7. Cada paso nuevo lleva su resultado y su verificación, como pide la plantilla. Revise el plan.md completo con la lista de chequeo (J.6) que está al final de `plantilla_plan.md` (en la carpeta de la sesión 2).

**Entregable.** El plan.md actualizado, con la lista de chequeo marcada. **Entrega:** la fecha se anuncia en clase.

**Criterios de evaluación**

| Criterio | Peso |
|---|---|
| Componente bien identificado (o ausencia bien justificada) | 35 % |
| Elección del tipo de modelo coherente con la guía de decisión | 35 % |
| Datos, privacidad y verificación considerados; plan.md que cumple la lista de chequeo | 30 % |

---

## Lectura obligatoria para la sesión 6

Krakovna, V., Uesato, J., Mikulik, V., Rahtz, M., Everitt, T., Kumar, R., Kenton, Z., Leike, J. y Legg, S. (2020, 21 de abril). *Specification gaming: the flip side of AI ingenuity*. Google DeepMind. <https://deepmind.google/blog/specification-gaming-the-flip-side-of-ai-ingenuity/>

Una entrada corta, con muchos ejemplos de sistemas que cumplen la métrica que se les puso sin cumplir el objetivo que se quería. Prepara la discusión sobre el aprendizaje por refuerzo de la Unidad 6.
