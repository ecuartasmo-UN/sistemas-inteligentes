# Sesión 4 · Trabajo independiente

**Sistemas Inteligentes · Especialización en Inteligencia Artificial · UNAL Manizales**
Unidad 4: Visualización Científica (Visión por Computador)

| Trabajo | Charla | Tipo | Tiempo estimado | Entrega |
|---|---|---|---|---|
| TI-1 · Diseñe la inspección visual de un proceso de su organización | Inicial · Procesamiento digital de imágenes | Ejercicio individual | 70 min | Inicio de la semana 3 |
| TI-2 · ¿Ven lo mismo CLIP y un LLM multimodal? | Intermedia · Del pipeline clásico a los modelos | Ejercicio individual | 70 min | Inicio de la semana 3 |
| Paso del proyecto integrador | De cierre · ¿Cuándo confiar en lo que ve una máquina? | En equipo | 60 min | Inicio de la semana 3 |
| **Total** | | | **3 h 20 min** | |

**Sobre el tiempo.** Cada sesión del bloque presencial genera unas 12 horas de trabajo independiente (Anexo A del programa). Estos dos trabajos y el paso del proyecto ocupan 3 h 20 min. El resto se dedica a terminar los laboratorios 4A y 4B y a la lectura de la sesión 5.

**Ninguno pide programar.** Se hacen con una cámara o un celular, un LLM multimodal, una hoja de cálculo y los notebooks de los laboratorios, cambiando imágenes y parámetros en sus celdas de configuración.

**Formato de entrega.** Un archivo PDF por trabajo, por el canal del curso. Los dos trabajos son individuales; el paso del proyecto es del equipo. Puede usar asistentes de IA generativa como herramienta de consulta, declarando cómo los usó; en el TI-2 el LLM es parte del ejercicio.

**Imágenes sin datos personales.** Las fotografías de estos trabajos **no deben mostrar personas** (ni rostros ni partes del cuerpo), documentos con datos personales, placas de vehículos ni información confidencial de su organización. Un rostro es un dato biométrico, y la Ley 1581 de 2012 lo trata como dato sensible. Si su proceso involucra personas, fotografíe solo los objetos o use imágenes simuladas.

---

## TI-1 · Diseñe la inspección visual de un proceso de su organización

**Charla inicial · 70 minutos**

**Propósito.** Practicar el diseño de un pipeline clásico de procesamiento de imágenes, etapa por etapa, sobre un problema real, y comprobar cuánto depende de la adquisición, como en el Laboratorio 4A.

**Instrucciones**

1. Elija un proceso de su organización en el que contar, medir o detectar defectos a partir de una imagen sea útil. Por ejemplo, productos en una bandeja, piezas en un almacén, cajas en un estante, frutos o granos, o formularios sin datos personales.
2. Tome de 5 a 10 fotografías con un celular, sin personas. Tome al menos dos con una luz distinta (por ejemplo, junto a una ventana y con luz artificial), o con otro fondo.
3. Diseñe el pipeline en una tabla con las etapas de la charla inicial:
   - **Adquisición:** qué controlaría (luz, fondo, distancia, ángulo) y por qué.
   - **Preproceso:** qué ajustaría (contraste, ruido, color).
   - **Segmentación:** cómo separaría el objeto del fondo.
   - **Descripción y medición:** qué mediría (cantidad, área, color, forma).
   - **Decisión:** qué regla aplicaría (por ejemplo, «rechazar si el área es menor que…»).
4. Pruebe su pipeline con sus fotografías en el notebook del Laboratorio 4A, cambiando solo la imagen y los parámetros en sus celdas de configuración. Anote, para cada foto, el resultado del pipeline y el conteo o la medida hechos a mano.
5. Compare las fotografías con distinta luz o fondo: ¿cambió el resultado? ¿Qué parámetro tuvo que ajustar?
6. Responda en media página:
   - ¿En qué etapa falló más su pipeline, y por qué?
   - ¿Qué cambio en la adquisición mejoraría más el resultado?
   - Con la guía de decisión de la charla de cierre: ¿bastaría un pipeline clásico para este proceso, o haría falta un modelo preentrenado?

**Entregable.** PDF de 1 a 2 páginas con dos o tres de sus fotografías, la tabla del pipeline, la tabla de resultados (pipeline frente a conteo a mano) y la reflexión.

**Criterios de evaluación**

| Criterio | Peso |
|---|---|
| Pipeline bien diseñado: cada etapa con su propósito y sus parámetros | 35 % |
| Prueba con fotografías propias, comparada con un conteo o una medida a mano | 40 % |
| Reflexión sobre la adquisición y sobre la elección de la técnica | 25 % |

**Apoyo**
- La charla inicial de esta sesión, en particular las diapositivas «Las etapas del procesamiento» e «Histograma, umbral y morfología: contar».
- Un caso real y cercano: Castrillón, Sanz y Ramos (2017), [«Visión artificial para identificar café lavado afectado por la broca»](https://biblioteca.cenicafe.org/bitstream/10778/1081/1/arc068%2802%297-19.pdf), *Revista Cenicafé* 68(2). Muestra cómo se controló la luz y qué eficacia se logró con un pipeline clásico.
- Szeliski, R. (2022). [*Computer Vision: Algorithms and Applications*, 2.ª ed.](https://szeliski.org/Book/), cap. 3, «Image Processing». Libro gratuito para uso personal, en inglés.

---

## TI-2 · ¿Ven lo mismo CLIP y un LLM multimodal?

**Charla intermedia · 70 minutos**

**Propósito.** Comparar dos formas de reconocer imágenes con modelos preentrenados, como en el Laboratorio 4B: CLIP, que clasifica escribiendo las clases como frases, y un LLM multimodal, al que se le pregunta por la imagen.

**Instrucciones**

1. Elija un problema de clasificación de su organización con 2 a 4 clases: por ejemplo, producto conforme o con defecto, tipo de empaque, estado de una instalación. Reúna de 10 a 20 imágenes propias, sin personas, y anote la clase real de cada una.
2. **Con CLIP:** en el notebook del Laboratorio 4B, cambie las imágenes y escriba cada clase como una frase («una foto de un empaque roto»). Pruebe dos redacciones distintas de las frases y anote cuál funciona mejor.
3. **Con un LLM multimodal** (Claude, Gemini o ChatGPT): envíe cada imagen con una instrucción como esta:

   > Clasifica esta imagen en una de estas clases: [clase 1], [clase 2], [clase 3]. Responde solo con el nombre de la clase y, en una línea, qué viste para decidir.

4. Construya la **matriz de confusión** de cada método en una hoja de cálculo: filas para la clase real, columnas para la clase asignada. Calcule la exactitud.
5. Estime el **costo** de clasificar 1000 imágenes con el LLM, con su tamaño de imagen y los precios oficiales, y compárelo con CLIP, que corre en su computador.
6. Revise las explicaciones del LLM en los casos que falló: ¿lo que dice haber visto está en la imagen?
7. Responda en media página:
   - ¿Qué método acertó más, y en qué clases falló cada uno?
   - ¿Cambiar las frases cambió el resultado de CLIP?
   - Con la guía de decisión: ¿cuál usaría en su organización, considerando costo, volumen, privacidad de las imágenes y explicación?

**Entregable.** PDF de 1 a 2 páginas con las clases y las frases, las dos matrices de confusión, el cálculo de costo, dos ejemplos de error explicados y la reflexión.

**Criterios de evaluación**

| Criterio | Peso |
|---|---|
| Conjunto de imágenes bien etiquetado y clases bien definidas | 25 % |
| Matrices de confusión y costo calculados correctamente | 40 % |
| Análisis de errores y reflexión con los conceptos de la sesión: características aprendidas, clasificación sin entrenamiento previo, costo por imagen | 35 % |

**Para leer con criterio.** Diez o veinte imágenes no bastan para elegir un sistema de producción: sirven para entender cómo se equivoca cada método. Una decisión real exige muchas más imágenes, tomadas en las condiciones de operación.

**Apoyo**
- Radford, A. et ál. (2021), [CLIP](https://proceedings.mlr.press/v139/radford21a.html): lo que dice sobre las plantillas de frases («A photo of a {label}.»). Es la lectura de esta sesión.
- Si el notebook no corre en su equipo, una demostración de CLIP en el navegador, sin instalar nada: [compare_clip_siglip](https://huggingface.co/spaces/merve/compare_clip_siglip), en Hugging Face. Se sube una imagen, se escriben las clases separadas por comas y muestra las tres más probables según CLIP y según SigLIP. Es un servicio de terceros: no suba imágenes confidenciales de su organización.
- Opcional, para ir más allá: [Teachable Machine](https://teachablemachine.withgoogle.com/), de Google, entrena un clasificador con sus propias imágenes, sin programar. Según el sitio, el entrenamiento ocurre en el navegador. Puede compararlo con CLIP, que no necesita ejemplos.
- Documentación oficial de visión, con el cálculo de tokens por imagen: [Anthropic](https://platform.claude.com/docs/en/build-with-claude/vision), [OpenAI](https://developers.openai.com/api/docs/guides/images-vision) y [Google Gemini](https://ai.google.dev/gemini-api/docs/media-resolution). Precios: [Anthropic](https://platform.claude.com/docs/en/about-claude/pricing), [OpenAI](https://developers.openai.com/api/docs/pricing) y [Google](https://ai.google.dev/gemini-api/docs/pricing).

---

## Paso del proyecto integrador

**Charla de cierre · en equipo · 60 minutos**

**Propósito.** Llevar la Unidad 4 al caso del proyecto: identificar si tiene un componente perceptual y, si lo tiene, cómo se resolvería y con qué restricciones.

**Instrucciones**

1. Revise el caso del proyecto con quien conoce el proceso en la organización: ¿hay **imágenes**, documentos escaneados, video o sensores que el sistema podría usar?
2. Si los hay, agregue al plan.md un paso para describir el componente perceptual: qué entra (la imagen o la señal), qué sale (un conteo, una etiqueta, una medida) y qué decisión apoya.
3. Agregue un paso para **elegir la técnica** con la guía de decisión de la charla de cierre (pipeline clásico, modelo preentrenado, LLM multimodal o modelo propio), y justifique la elección por datos disponibles, control de la adquisición, costo y explicabilidad.
4. Agregue un paso sobre **datos y privacidad**: de dónde saldrán las imágenes, si muestran personas y qué autorización hace falta.
5. Si el caso no tiene un componente perceptual, explique en el plan.md por qué, en un párrafo.
6. Cada paso nuevo lleva su resultado y su verificación, como pide la plantilla. Revise el plan.md completo con la lista de chequeo (J.6) que está al final de `plantilla_plan.md` (en la carpeta de la sesión 2).

**Entregable.** El plan.md actualizado, con la lista de chequeo marcada.

**Criterios de evaluación**

| Criterio | Peso |
|---|---|
| Componente perceptual bien identificado (o ausencia bien justificada) | 35 % |
| Elección de la técnica coherente con la guía de decisión | 35 % |
| Datos y privacidad considerados; plan.md que cumple la lista de chequeo | 30 % |

---

## Lectura obligatoria para la sesión 5

Alammar, J. (2018, 27 de junio). *The Illustrated Transformer*. <https://jalammar.github.io/illustrated-transformer/>

Es una explicación visual de la arquitectura propuesta en *Attention Is All You Need*; se lee junto con las figuras del artículo original.
