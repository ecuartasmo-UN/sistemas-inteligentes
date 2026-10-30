# Sesión 6 · Trabajo independiente

**Sistemas Inteligentes · Especialización en Inteligencia Artificial · UNAL Manizales**
Unidad 6: Aprendizaje de Máquina

| Trabajo | Charla | Tipo | Tiempo estimado | Entrega |
|---|---|---|---|---|
| TI-1 · ¿Redescubre un árbol su sistema experto? | Inicial · Del dato al conocimiento | Ejercicio individual | 70 min | Inicio de la semana 4 |
| TI-2 · Un indicador que se cumple sin cumplir el objetivo | Intermedia · El agente que aprende por refuerzo | Ejercicio individual | 65 min | Inicio de la semana 4 |
| Paso del proyecto del curso | De cierre · Aprender en los sistemas inteligentes | En equipo | 60 min | La fecha se anuncia en clase |
| **Total** | | | **3 h 15 min** | |

**Sobre el tiempo.** Cada sesión del bloque presencial genera unas 12 horas de trabajo independiente (Anexo A del programa). Estos dos trabajos y el paso del proyecto ocupan 3 h 15 min. El resto se dedica a terminar los laboratorios 6A y 6B y a la lectura de la sesión 7.

**Ninguno pide programar.** Se hacen con una hoja de cálculo, con una demostración en el navegador y con los notebooks de los laboratorios, cambiando datos y parámetros en sus celdas de configuración.

**Formato de entrega.** Un archivo PDF por trabajo, por el canal del curso. Los dos trabajos son individuales; el paso del proyecto es del equipo. Puede usar asistentes de IA generativa como herramienta de consulta, declarando cómo los usó.

**Sin datos personales.** Los casos y descripciones de estos trabajos **no deben contener datos personales** (nombres, documentos, teléfonos, correos, direcciones) ni información confidencial de su organización. Si parte de casos reales, cámbieles los datos que identifiquen a una persona, un cliente o un proveedor antes de usarlos.

---

## TI-1 · ¿Redescubre un árbol su sistema experto?

**Charla inicial · 70 minutos**

**Propósito.** En el TI-1 de la Sesión 1 usted escribió a mano las reglas de un sistema experto para una decisión de su organización. Ahora va a comprobar qué parte de ese conocimiento puede aprender un árbol de decisión a partir de casos, y qué parte no: es la comparación entre el experto y los datos que vimos en la charla inicial y en el Laboratorio 6A.

**Instrucciones**

1. Retome las reglas de su TI-1 de la Sesión 1. Si no lo hizo, elija una decisión de su organización que dependa de 3 a 6 datos, como aprobar una solicitud, priorizar una orden o diagnosticar una falla, y escriba de 6 a 8 reglas SI… ENTONCES.
2. En una hoja de cálculo, cree una columna por cada dato que usan sus reglas (de 3 a 6) y una última columna, `conclusion`, con la decisión. Use valores sencillos: números o categorías cortas, como «alta», «media» y «baja».
3. Escriba **de 40 a 60 casos**, uno por fila, con la conclusión que daría un experto. Incluya casos frontera y excepciones que conozca por experiencia, no solo los que dictan sus reglas. Si tiene casos históricos, úselos sin datos personales.
   > Si escribe la conclusión aplicando sus reglas al pie de la letra, el árbol solo las copiará. Lo interesante aparece con las excepciones y con los casos en que el experto no seguiría la regla.
4. Guarde la hoja como CSV y cárguela en la sección **«Sus propios datos»** del notebook del Laboratorio 6A. Induzca árboles de profundidad 2, 3 y 4, y anote el acierto con validación cruzada de cada uno.
5. Elija una profundidad y copie las reglas que imprime el árbol. Compárelas con las suyas en una tabla de tres columnas:
   - **coinciden:** el árbol aprendió la misma regla, o una equivalente;
   - **faltan:** están en sus reglas, pero no en el árbol;
   - **sobran:** están en el árbol, pero no en sus reglas.
6. **Estabilidad.** Quite 5 casos al azar, vuelva a inducir el árbol y anote si cambian las reglas. Con pocos casos, un árbol puede cambiar mucho.
7. Responda en media página:
   - ¿Qué conocimiento redescubrió el árbol, cuál no pudo y por qué? Piense en los casos que nunca escribió.
   - ¿Qué pondría a funcionar en su organización: sus reglas, el árbol o los dos? Use la guía de decisión de la charla de cierre.
   - Si un auditor pregunta «¿por qué se tomó esta decisión?», ¿qué respondería con sus reglas y qué con el árbol?

**Entregable.** PDF de 1 a 2 páginas con sus reglas, una muestra de 10 casos, la tabla de aciertos por profundidad, las reglas del árbol, la tabla de comparación, el resultado de la prueba de estabilidad y la reflexión. Adjunte el CSV.

**Criterios de evaluación**

| Criterio | Peso |
|---|---|
| Casos bien construidos: variables claras, excepciones incluidas, sin datos personales | 30 % |
| Árboles inducidos y evaluados con validación cruzada; comparación de reglas completa | 40 % |
| Reflexión con los conceptos de la sesión: sobreajuste, interpretabilidad y lo que los datos no muestran | 30 % |

**Para leer con criterio.** Cincuenta casos escritos por una persona no reemplazan los datos de la operación: el árbol aprende lo que usted escribió, con sus sesgos. El ejercicio sirve para ver cómo se relacionan las reglas del experto con las que se inducen de los datos, no para validar un sistema.

**Apoyo**
- La charla inicial de esta sesión, en particular «Cada camino del árbol es una regla» y «Un árbol sin límite memoriza».
- Su propio TI-1 de la Sesión 1 y la presentación de sistemas expertos de esa sesión.
- Yee, S. y Chu, T. (2015). [*Una introducción visual al machine learning*](https://r2d3.us/una-introduccion-visual-al-machine-learning-1/), R2D3. Un árbol de decisión que crece paso a paso, en español.
- Wilber, J. y Santamaría, L. [*Decision Trees*](https://mlu-explain.github.io/decision-tree/), MLU-Explain (Amazon), CC BY-SA 4.0. Entropía, ganancia de información y sobreajuste, en inglés.
- Poole, D. L. y Mackworth, A. K. (2023). [*Artificial Intelligence: Foundations of Computational Agents*](https://artint.info/3e/html/ArtInt3e.Ch7.S3.html), 3.ª ed., sección 7.3 (árboles de decisión). Libro abierto, en inglés.

---

## TI-2 · Un indicador que se cumple sin cumplir el objetivo

**Charla intermedia · 65 minutos**

**Propósito.** Ver en una demostración cómo la recompensa decide la conducta de un agente, y llevarlo a un indicador de su organización: cómo podría cumplirse sin cumplir su propósito y qué supervisión lo evitaría.

**Instrucciones**

1. Abra [REINFORCEjs · GridWorld: Dynamic Programming](https://cs.stanford.edu/people/karpathy/reinforcejs/gridworld_dp.html), de Andrej Karpathy (licencia MIT). Corre en el navegador, sin instalar nada. Es una cuadrícula de 10 × 10 con muros, una meta que vale +1 y algunas casillas que valen −1; el descuento es 0,9. Si el sitio no abre, descargue el repositorio de [GitHub](https://github.com/karpathy/reinforcejs) con *Code → Download ZIP*, descomprímalo y abra `gridworld_dp.html` con su navegador.
2. **La iteración de valores.** Pulse *Toggle Value Iteration* y espere a que los colores y las flechas dejen de cambiar. Haga una captura y describa en dos líneas la política: ¿por dónde llega a la meta?
3. **Cambiar la recompensa.** Seleccione una casilla y cambie su recompensa con el deslizador *Cell reward*:
   - ponga una casilla con recompensa positiva cerca del inicio, lejos de la meta, y observe si el agente sigue yendo a la meta;
   - ponga varias casillas con −1 en el camino más corto y observe el desvío.

   Anote en una tabla cada cambio, la conducta que esperaba y la que obtuvo.
4. **Aprender sin modelo.** Abra [TDDemo](https://www.cs.cmu.edu/~dst/TDDemo/), de Yifei Chen y Dave Touretzky (Carnegie Mellon), basada en REINFORCEjs. Pulse *Run* y observe cómo el agente explora y mejora su política; con *Single Step* puede seguirlo paso a paso. Cuando la haya encontrado, cambie la recompensa de una casilla con *Edit Reward* y describa cuánto le cuesta corregirse. Pruebe también el deslizador *Exploration epsilon*: ¿qué pasa si el agente casi no explora?
5. **Su organización como MDP.** Elija una decisión de su organización que se toma en secuencia, como cuándo hacer mantenimiento, cuánto inventario pedir o cómo asignar turnos. Descríbala con las cinco piezas de la charla: estados, acciones, qué tan inciertos son sus resultados, recompensas y si el futuro pesa menos que el presente. Dibuje un diagrama sencillo, como el de la bomba de MantenIA.
6. **El indicador.** Identifique el indicador con el que hoy se mide esa decisión. Describa al menos una forma en que podría **cumplirse sin cumplir su propósito**. No use los ejemplos de la lectura de la sesión ni los de las charlas: busque uno propio de su área.
7. Responda en media página: ¿qué supervisión o qué segundo indicador lo evitaría? ¿Quién lo notaría si ocurre, y cuánto tardaría en notarlo?

**Entregable.** PDF de 1 a 2 páginas con las dos capturas de la demostración, la tabla de cambios de recompensa, el MDP de su organización con su diagrama, el análisis del indicador y la reflexión.

**Criterios de evaluación**

| Criterio | Peso |
|---|---|
| Experimentos con la demostración bien registrados e interpretados | 30 % |
| MDP de su organización completo y coherente con las cinco piezas | 35 % |
| Análisis del indicador: forma de engañarlo, supervisión propuesta, sin repetir los ejemplos de la lectura | 35 % |

**Apoyo**
- La charla intermedia de esta sesión, en particular «Otra recompensa, otra conducta» y «La recompensa es la especificación».
- Sutton, R. S. y Barto, A. G. (2018). [*Reinforcement Learning: An Introduction*](http://incompleteideas.net/book/the-book-2nd.html), 2.ª ed., capítulos 3 y 4 (MDP y programación dinámica). Libro abierto, en inglés.
- Si prefiere una demostración en español: [Aprendizaje por refuerzo](https://imaginary.github.io/reinforcement-learning-2/exhibit.html?lang=es), de IMAGINARY (licencia MIT). Se dibuja el laberinto y se ve cómo aprende el agente, aunque las recompensas son fijas por tipo de casilla.

---

## Paso del proyecto del curso

**Charla de cierre · en equipo · 60 minutos**

**Propósito.** Llevar la Unidad 6 al proyecto del equipo, que es libre y se construye con vibe coding: analizar los riesgos de automatizar una decisión y la supervisión que requiere.

**Instrucciones**

1. Identifique **la decisión** que su proyecto automatiza o apoya, y quién la toma hoy.
2. Agregue al plan.md un paso que defina **el indicador** con el que se medirá si el sistema funciona: qué se cuenta, con qué datos y cada cuánto.
3. Agregue un paso que analice cómo ese indicador podría **cumplirse sin cumplir el objetivo**. Escriba al menos un escenario concreto, como el bote que gira sobre una flecha o las órdenes cerradas sin resolver.
4. Agregue un paso sobre **la supervisión**: qué revisa una persona, qué verifica otra técnica (una regla, un caso de prueba, un segundo indicador) y qué hace el sistema cuando no está seguro.
5. Si su proyecto aprende de datos, agregue un paso sobre **cómo se evaluará**: con qué separación de datos o validación cruzada, y qué error cuesta más.
6. Cada paso nuevo lleva su resultado y su verificación, como pide la plantilla. Revise el plan.md completo con la lista de chequeo (J.6) que está al final de `plantilla_plan.md` (en la carpeta de la sesión 2).

**Entregable.** El plan.md actualizado, con la lista de chequeo marcada. **Entrega:** la fecha se anuncia en clase.

**Criterios de evaluación**

| Criterio | Peso |
|---|---|
| Decisión e indicador bien definidos | 30 % |
| Escenario de indicador engañado, concreto y plausible | 35 % |
| Supervisión y evaluación coherentes; plan.md que cumple la lista de chequeo | 35 % |

---

## Lectura obligatoria para la sesión 7

Pearl, J. (2019). The seven tools of causal inference, with reflections on machine learning. *Communications of the ACM*, 62(3), 54–60. <https://web.archive.org/web/20250622142952/https://cacm.acm.org/research/the-seven-tools-of-causal-inference-with-reflections-on-machine-learning/> (copia en Wayback Machine; versión abierta: <https://ftp.cs.ucla.edu/pub/stat_ser/r481.pdf>)

Un artículo corto sobre lo que el aprendizaje de máquina no puede responder solo con datos: distinguir una correlación de una causa. Prepara la Unidad 7, sobre la decisión bajo incertidumbre.
