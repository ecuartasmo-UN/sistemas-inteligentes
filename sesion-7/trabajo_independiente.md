# Sesión 7 · Trabajo independiente

**Sistemas Inteligentes · Especialización en Inteligencia Artificial · UNAL Manizales**
Unidad 7: Razonamiento bajo Incertidumbre y Toma de Decisiones

| Trabajo | Charla | Tipo | Tiempo estimado | Entrega |
|---|---|---|---|---|
| TI-1 · ¿Cuánto pagarías por saber antes de decidir? | Inicial · Creer con evidencia, y decidir | Ejercicio individual | 70 min | Fase de cierre |
| TI-2 · Diseña el tutor de un curso de tu organización | Intermedia · El tutor que estima lo que sabes | Ejercicio individual | 65 min | Fase de cierre |
| Paso del proyecto del curso | De cierre · Decidir bajo incertidumbre en las organizaciones | En equipo | 60 min | La fecha se anuncia en clase |
| **Total** | | | **3 h 15 min** | |

**Sobre el tiempo.** Cada sesión del bloque presencial genera unas 12 horas de trabajo independiente (Anexo A del programa). Estos dos trabajos y el paso del proyecto ocupan 3 h 15 min. El resto es para terminar los laboratorios 7A y 7B y para la lectura de la sesión 8.

**Ninguno pide programar.** Los haces con una hoja de cálculo, con una herramienta en el navegador o con los notebooks de los laboratorios. En los notebooks solo cambias datos y parámetros en las celdas de configuración.

**Formato de entrega.** Un archivo PDF por trabajo, por el canal del curso. Los dos trabajos son individuales; el paso del proyecto es del equipo. Puedes usar asistentes de IA generativa como herramienta de consulta. Si lo haces, di cómo los usaste.

**Cuándo se entregan.** Los trabajos de la semana 4 se entregan en la fase de cierre (Anexo D del programa). Es hasta 2 semanas después de la sesión 8. La fecha exacta se anuncia en clase.

**Sin datos personales.** Tus casos y descripciones **no deben tener datos personales**: nombres, documentos, teléfonos, correos ni direcciones. Tampoco información confidencial de tu organización. Si partes de casos reales, cambia los datos que identifiquen a una persona, un cliente o un proveedor.

---

## TI-1 · ¿Cuánto pagarías por saber antes de decidir?

**Charla inicial · 70 minutos**

**Propósito.** En la charla inicial y en el Laboratorio 7A viste el problema del petrolero. Una prueba sísmica valía 12.5 y costaba 10, así que convenía hacerla. Ahora vas a hacer la misma cuenta con una decisión de tu organización.

**Instrucciones**

1. Elige una decisión de tu organización con un resultado incierto. Por ejemplo: lanzar un producto, aprobar una compra grande o reemplazar un equipo. Usa 2 o 3 opciones y de 2 a 4 resultados posibles.
2. Para cada resultado, estima su probabilidad. Las probabilidades deben sumar 1. Escribe en una línea de dónde sale cada una: datos históricos, la opinión de un experto o una suposición.
3. Asigna una utilidad a cada combinación de opción y resultado. Puede ser dinero o una escala de 0 a 100. Una pérdida es una utilidad negativa.
4. En una hoja de cálculo, calcula la utilidad esperada de cada opción: la suma de probabilidad por utilidad. Anota qué opción eliges.
5. Piensa en una información que podrías comprar antes de decidir: un estudio de mercado, una prueba piloto o una inspección.
   - Escribe qué tan confiable es: con qué probabilidad da cada resultado, según lo que de verdad pase.
   - Calcula la utilidad esperada si decides después de ver esa información. Usa la tabla del petrolero como modelo.
   - La diferencia con el paso 4 es **el valor de la información**. Compáralo con su precio.
6. **Sensibilidad.** Elige la probabilidad que más dudas te da. Súbela y bájala un 20 %. ¿Cambia la decisión? ¿Cambia el valor de la información?
7. Responde en media página:
   - ¿Vale la pena comprar la información? ¿Por qué?
   - ¿Qué número de tu modelo es el más débil, y cómo lo mejorarías?
   - ¿Qué parte de la decisión no cabe en la cuenta, y quién debería pesarla?

**Entregable.** PDF de 1 a 2 páginas con la tabla de opciones, resultados, probabilidades y utilidades. Incluye la utilidad esperada de cada opción, el valor de la información, la prueba de sensibilidad y la reflexión. Adjunta la hoja de cálculo.

**Criterios de evaluación**

| Criterio | Peso |
|---|---|
| Decisión bien planteada: opciones, resultados, probabilidades justificadas y utilidades coherentes | 30 % |
| Utilidad esperada y valor de la información bien calculados | 40 % |
| Sensibilidad y reflexión con los conceptos de la sesión: tasa base, valor de la información y límites del modelo | 30 % |

**Para leer con criterio.** Tus probabilidades y utilidades son estimaciones. El modelo no te da la respuesta correcta: te muestra qué supuestos mueven la decisión. Por eso la prueba de sensibilidad importa tanto como la cuenta.

**Apoyo**
- La charla inicial de esta sesión. Mira en particular «Decidir: la utilidad esperada» y «¿Cuánto pagarías por saber antes de decidir?».
- El notebook del Laboratorio 7A, con el diagrama de influencia del petrolero.
- [SilverDecisions](https://silverdecisions.pl/), de la Escuela de Economía de Varsovia (SGH). Arma árboles de decisión en el navegador, sin instalar nada, y calcula el valor esperado. Licencia LGPL v3. Está en inglés. Para el valor de la información, arma el árbol con la información y resta los dos valores. Guarda tu árbol en JSON y expórtalo en PNG.
- Szufel, P., Jakubczyk, M. y Kamiński, B. (eds.) (2022). [*Modeling Decision Trees with SilverDecisions*](https://szufel.pl/Modeling_Decision_Trees_with_SilverDecisions_2022_edited_by_P_Szufel_M_Jakubczyk_B_Kaminski.pdf). SGH Publishing House. La sección 4.1 explica el valor de la información con ejemplos. En inglés.
- Si quieres explorar un diagrama de influencia ya armado: el modelo «VentureEVPI» de [BayesBox](https://repo.bayesfusion.com/bayesbox.html), de BayesFusion. Puedes poner evidencia y decisiones sin registrarte.
- Poole, D. L. y Mackworth, A. K. (2023). [*Artificial Intelligence: Foundations of Computational Agents*](https://artint.info/3e/html/ArtInt3e.Ch12.html), 3.ª ed., cap. 12, en particular la sección 12.4 sobre el valor de la información. Libro abierto, en inglés.

---

## TI-2 · Diseña el tutor de un curso de tu organización

**Charla intermedia · 65 minutos**

**Propósito.** En la charla intermedia y en el Laboratorio 7B viste un tutor que estima qué domina cada técnico. Ahora vas a diseñar el modelo del estudiante para un curso de tu organización.

**Instrucciones**

1. Elige un curso de formación de tu organización. Por ejemplo: la inducción de personal nuevo, un curso de seguridad o el uso de un software.
2. Define de 3 a 5 habilidades. Es el modelo del dominio. Para cada una, escribe un ejercicio de ejemplo.
3. Para cada habilidad, propone los cuatro parámetros de *Bayesian Knowledge Tracing*, con una línea de justificación:
   - el dominio inicial: con qué dominio llega la persona;
   - el aprendizaje: cuánto aprende en cada práctica;
   - la adivinanza: cuánto acierta sin dominar;
   - el descuido: cuánto falla aunque domine.

   Usa valores razonables. La adivinanza va entre 0 y 0.3, y el descuido entre 0 y 0.1 (Baker, Corbett y Aleven, 2008). Si son más altos, el modelo deja de tener sentido.
4. Inventa secuencias de 8 a 12 respuestas (✓ o ✗) para tres estudiantes ficticios:
   - uno que ya domina la habilidad al llegar;
   - uno que aprende a mitad del camino;
   - uno que acierta varias veces por adivinar.
5. Carga tus habilidades, tus parámetros y tus secuencias en la sección del notebook del 7B para tus propios datos. Anota la curva de dominio de cada estudiante. Anota también cuántos ejercicios necesita cada uno con la regla de dominio de 0.95.
6. Cambia el umbral a 0.85 y a 0.99. ¿Qué gana y qué pierde el tutor en cada caso?
7. Responde en media página:
   - ¿Qué decidiría el tutor con cada estudiante? ¿Estás de acuerdo?
   - ¿Qué riesgos tendría un tutor con un LLM en este curso? Usa el estudio de Bastani et al. (2025) de la charla intermedia.
   - ¿Qué supervisión humana necesita el tutor antes de habilitar a alguien?

**Entregable.** PDF de 1 a 2 páginas con las habilidades, los parámetros justificados y las secuencias. Incluye las curvas de dominio, la prueba del umbral y la reflexión.

**Criterios de evaluación**

| Criterio | Peso |
|---|---|
| Modelo del dominio claro, con habilidades y ejercicios concretos | 25 % |
| Parámetros justificados y secuencias que prueban los tres tipos de estudiante | 35 % |
| Reflexión con los conceptos de la sesión: el estado oculto, el umbral, los riesgos del LLM y la supervisión | 40 % |

**Para leer con criterio.** Tú inventas las secuencias, así que el tutor solo refleja tus supuestos. Un tutor real necesita estimar los parámetros con datos de muchas personas, con su consentimiento.

**Apoyo**
- La charla intermedia de esta sesión, en particular «Cuatro números describen al estudiante» y «La curva de dominio».
- El notebook del Laboratorio 7B.
- [BKT Balloon](https://catherinesyeh.github.io/bkt-balloon/), de Catherine Yeh e Iris Howley (Williams College). Mueve los cuatro parámetros y responde bien o mal: un globo sube con el dominio estimado. Licencia GPL-3.0. En inglés.
- Corbett, A. T. y Anderson, J. R. (1994). [Knowledge tracing: modeling the acquisition of procedural knowledge](https://doi.org/10.1007/BF01099821). *User Modeling and User-Adapted Interaction* 4(4), 253–278. El artículo original del modelo, en inglés.

---

## Paso del proyecto del curso

**Charla de cierre · en equipo · 60 minutos**

**Propósito.** Hacer el cierre técnico del proyecto antes de la sesión 8. El proyecto es libre y se construye con vibe coding. En este paso, el equipo define dónde aparece la incertidumbre, cuál es su componente híbrido y qué va a mostrar.

**Instrucciones**

1. Identifica **dónde aparece la incertidumbre** en tu proyecto. Puede venir de datos incompletos, de respuestas de un LLM o de resultados imprevisibles. Agrega al plan.md un paso que diga cómo la manejan o cómo se la comunican al usuario.
2. Define **el componente híbrido**: qué propone el LLM y qué técnica clásica, prueba o persona lo verifica. Agrega un paso al plan.md con su resultado y su verificación.
3. Planea **la sustentación** de la sesión 8, con la [guía de la sustentación](https://github.com/ecuartasmo-UN/sistemas-inteligentes/blob/main/sesion-8/sustentacion_proyecto.md). Define qué caso vas a mostrar, qué debe pasar y qué haces si algo falla.
4. Si tu sistema decide o recomienda, agrega un paso que diga con qué criterio lo hace. ¿Usa una probabilidad, una utilidad o una regla?
5. Cada paso nuevo lleva su resultado y su verificación, como pide la plantilla. Revisa el plan.md completo con la lista de chequeo (J.6). Está al final de `plantilla_plan.md`, en la carpeta de la sesión 2.

**Entregable.** El plan.md actualizado, con la lista de chequeo marcada. **Entrega:** la fecha se anuncia en clase.

**Criterios de evaluación**

| Criterio | Peso |
|---|---|
| La incertidumbre del proyecto bien identificada, con una forma de manejarla | 30 % |
| Un componente híbrido con su verificación | 35 % |
| Una sustentación planeada; plan.md que cumple la lista de chequeo | 35 % |

---

## Lectura obligatoria para la sesión 8

Se leen en par, para discutir por qué hay que verificar:

- Shojaee, P., Mirzadeh, I., Alizadeh, K., Horton, M., Bengio, S. y Farajtabar, M. (2025). The illusion of thinking: understanding the strengths and limitations of reasoning models via the lens of problem complexity. *NeurIPS 2025*. <https://arxiv.org/abs/2506.06941>
- Lawsen, A. (2025). Comment on The Illusion of Thinking: understanding the strengths and limitations of reasoning models via the lens of problem complexity. arXiv. <https://arxiv.org/abs/2506.09250>

El primero sostiene que los modelos de razonamiento fallan cuando el problema se vuelve complejo. El segundo cuestiona cómo se midió. Prepara la sesión 8, sobre los sistemas híbridos y la verificación.
