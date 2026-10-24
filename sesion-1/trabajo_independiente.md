# Sesión 1 · Trabajo independiente

**Sistemas Inteligentes · Especialización en Inteligencia Artificial · UNAL Manizales**
Unidad 1: Inteligencia Artificial (IA), Sistemas Expertos (SE), IA Distribuida & Sistemas Multi-Agente (SMA)

| Trabajo | Bloque | Tipo | Tiempo estimado | Entrega |
|---|---|---|---|---|
| TI-1 · Su propio sistema experto en papel | 1 · IA y sistemas expertos | Ejercicio | 75 min | Inicio de la semana 2 |
| TI-2 · Un agente para su organización | 2 · IA distribuida y agentes | Ejercicio | 60 min | Inicio de la semana 2 (idealmente antes de la sesión 2) |
| TI-3 · ¿Cuándo conviene un sistema multiagente con LLMs? | 3 · Sistemas multiagente | Lectura con preguntas guía | 90 min | Inicio de la semana 2 |
| **Total** | | | **3 h 45 min** | |

**Sobre el tiempo.** Cada sesión del bloque presencial genera unas 12 horas de trabajo independiente (Anexo A del programa). Estos tres trabajos ocupan 3 h 45 min. El resto se dedica a terminar el curso [Claude 101](https://anthropic.skilljar.com/claude-101), avanzar el proyecto integrador y preparar la lectura de la sesión 2.

**Formato de entrega.** Un archivo PDF por trabajo, por el canal del curso. Los trabajos son individuales. Puede usar asistentes de IA generativa como herramienta de consulta, declarando cómo los usó; el razonamiento y las trazas deben ser suyos.

---

## TI-1 · Su propio sistema experto en papel

**Bloque 1 · 75 minutos**

**Propósito.** Practicar la representación del conocimiento con reglas y el razonamiento hacia adelante y hacia atrás, sobre un problema de su propia organización.

**Instrucciones**

1. Elija una decisión recurrente de su organización que hoy dependa del criterio de una persona experta. Por ejemplo: aprobar una solicitud, clasificar un incidente, diagnosticar una falla o priorizar un pedido.
2. Escriba entre 6 y 8 reglas de la forma SI condiciones ENTONCES conclusión. Al menos dos reglas deben encadenarse: la conclusión de una es condición de otra.
3. Defina un caso concreto con 3 a 5 hechos iniciales.
4. **Encadenamiento hacia adelante.** Trace a mano cada ciclo: qué regla se dispara y qué hecho nuevo se agrega, hasta que no se pueda disparar ninguna regla más.
5. **Encadenamiento hacia atrás.** Elija una conclusión y dibuje el árbol de metas. Indique qué datos tendría que preguntar el sistema y en qué orden.
6. Redacte la pregunta «¿por qué?» que le haría un auditor sobre esa decisión y la respuesta que daría la traza de su sistema.

**Entregable.** PDF de 1 a 2 páginas con las reglas, los hechos, la traza hacia adelante, el árbol hacia atrás y la pregunta del auditor con su respuesta.

**Criterios de evaluación**

| Criterio | Peso |
|---|---|
| Reglas bien formadas, sin contradicciones y con al menos un encadenamiento | 40 % |
| Trazas correctas en ambas direcciones | 40 % |
| Explicación clara y útil para un auditor | 20 % |

**Apoyo.** Poole, D. y Mackworth, A. (2023). *Artificial Intelligence: Foundations of Computational Agents* (3.ª ed.), sección 5.3, "Propositional Definite Clauses". Los procedimientos *bottom-up* y *top-down* corresponden al encadenamiento hacia adelante y hacia atrás. Texto abierto: <https://artint.info/3e/html/ArtInt3e.Ch5.S3.html>

---

## TI-2 · Un agente para su organización

**Bloque 2 · 60 minutos**

**Propósito.** Especificar un agente antes de construirlo y elegir su arquitectura a partir de las propiedades de su entorno.

**Instrucciones**

1. Identifique un proceso de su organización donde un agente de software podría **actuar**, no solo responder. Por ejemplo: programar, asignar, reabastecer o monitorear.
2. Especifique su **PEAS** en una tabla: medida de desempeño, entorno, actuadores y sensores. Sea concreto: ¿qué indicadores?, ¿qué sistemas?, ¿qué acciones?
3. Clasifique su entorno con las seis propiedades vistas en clase, con una frase de justificación para cada una: observable, determinista, episódico, estático, discreto y número de agentes.
4. Recomiende una arquitectura (reactiva, deliberativa, BDI o híbrida por capas) y justifique la elección a partir de la clasificación del entorno.

**Entregable.** PDF de 1 página: tabla PEAS, clasificación del entorno y justificación de la arquitectura.

**Criterios de evaluación**

| Criterio | Peso |
|---|---|
| PEAS completo y específico | 40 % |
| Clasificación del entorno justificada | 30 % |
| Coherencia entre el entorno y la arquitectura elegida | 30 % |

**Nota.** Este trabajo es insumo directo de la propuesta del proyecto integrador, que se entrega en la sesión 2. Si puede, termínelo antes de esa sesión.

**Apoyo.** Poole y Mackworth (2023):
- Capítulo 2, "Agent Architectures and Hierarchical Control": <https://artint.info/3e/html/ArtInt3e.Ch2.html>
- Sección 1.3, "Agents Situated in Environments": <https://artint.info/3e/html/ArtInt3e.Ch1.S3.html>

---

## TI-3 · ¿Cuándo conviene un sistema multiagente con LLMs?

**Bloque 3 · 90 minutos**

**Propósito.** Analizar con criterio la evidencia reciente sobre sistemas multiagente basados en LLMs, usando los conceptos clásicos de coordinación vistos en clase.

**Lecturas** (ambas en inglés y en acceso abierto)

1. Anthropic (13 de junio de 2025). *How we built our multi-agent research system*. Blog de ingeniería. Unos 40 minutos. <https://www.anthropic.com/engineering/multi-agent-research-system>
2. Cemri, M. et al. (2025). *Why Do Multi-Agent LLM Systems Fail?* NeurIPS 2025, Datasets and Benchmarks Track. **Lea solo la figura 1 y la sección 4.** Unos 30 minutos. <https://arxiv.org/abs/2503.13657>

**Preguntas guía.** Responda las tres en una página en total; dedique unos 20 minutos a escribir.

1. Según Anthropic, ¿qué tipo de tareas se benefician de repartir el trabajo entre varios agentes y cuáles no? ¿Compensa un consumo de tokens unas 15 veces mayor que el de una conversación normal?
2. Elija tres modos de falla de la taxonomía MAST de Cemri et al. Para cada uno, describa su equivalente en una organización humana y el mecanismo clásico de coordinación (roles, protocolos o verificación) que lo mitigaría.
3. ¿Qué problemas de los sistemas multiagente clásicos reaparecen con los LLMs y qué es realmente nuevo?

**Entregable.** PDF de 1 página con las tres respuestas.

**Criterios de evaluación**

| Criterio | Peso |
|---|---|
| Comprensión correcta de las dos lecturas | 30 % |
| Uso de los conceptos del bloque: roles, protocolos, coordinación y verificación | 40 % |
| Implicación organizacional concreta y lectura crítica de las fuentes | 30 % |

**Para leer con criterio.** El blog de Anthropic es una fuente corporativa que reporta una evaluación interna: su resultado de +90 % frente a un solo agente no ha sido replicado de forma independiente. Cemri et al. es un estudio revisado por pares, con más de 1.600 trazas de siete sistemas de código abierto.

---

## Lectura obligatoria para la sesión 2

Kambhampati, S. et al. (2024). *Position: LLMs Can't Plan, But Can Help Planning in LLM-Modulo Frameworks*. ICML 2024. <https://proceedings.mlr.press/v235/kambhampati24a.html>
