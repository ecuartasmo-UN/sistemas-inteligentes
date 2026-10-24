# SISTEMAS INTELIGENTES — Contenido actualizado 2026 (versión 4)

**Especialización en Inteligencia Artificial — Facultad de Administración — Universidad Nacional de Colombia, Sede Manizales**
Departamento de Informática y Computación · Asignatura obligatoria (Acuerdo 04 de 2025 del Consejo de Sede, art. 4)

---

## Análisis de cambios frente al programa original (2024)

Esta sección compara esta versión con el programa original de *Sistemas Inteligentes* (`SISTEMAS INTELIGENTES.xlsx`, diligenciado el 25 de octubre de 2024) y justifica cada cambio. El detalle tema por tema está en el Anexo I.

### Síntesis

El programa original tenía una base temática valiosa: sistemas expertos, sistemas multiagente, planificación, visión, redes neuronales, aprendizaje de máquina e IA en educación. Esa base se conserva. Sus problemas no estaban en la elección de los grandes temas sino en tres frentes:
- **Formato:** créditos no enteros, ausencia de resultados de aprendizaje, metodología y evaluación.
- **Estructura:** contenidos repetidos, temas mezclados entre unidades y actividades listadas como contenidos.
- **Actualización:** tecnologías de hace dos décadas y una bibliografía débil, en un momento en que la IA cambió de forma radical con los modelos de lenguaje.

Los cambios responden a cuatro criterios:
1. **Cumplir la normativa:** el Acuerdo 04 de 2025, que fija 4 créditos, y el Decreto 1330 de 2019, que exige créditos enteros.
2. **Cubrir lo que el Acuerdo 04 de 2025 promete en los perfiles y objetivos del programa:** aprendizaje profundo, visión, ética, sistemas basados en conocimiento, optimización e incertidumbre.
3. **Evitar duplicar otras asignaturas del plan:** *Aprendizaje de Máquinas*, *Optimización e IA* y *Agentes de IA (aplicado)*.
4. **Conectar cada técnica clásica con la IA actual,** en particular con los LLMs y los sistemas híbridos.

### Comparación general

| Aspecto | Programa original (2024) | Versión actual | Justificación |
|---|---|---|---|
| Intensidad y créditos | 2 HAP + 9 HAI = 11 h/semana × 16 = 176 h → **3,67 créditos** | 2 HAP + 10 HAI = 12 h/semana × 16 = 192 h → **4 créditos** | El Acuerdo 04 de 2025 asigna 4 créditos a cada obligatoria. El Decreto 1330 de 2019 (art. 2.5.3.2.4.2) exige créditos enteros, y la UNAL define 1 crédito = 48 h (Acuerdo 033 de 2007, art. 6). Ver Anexo H |
| Organización presencial | No especificada (32 h distribuidas por semana) | 8 sesiones de 4 h concentradas en **4 semanas** (2 sesiones por semana). El trabajo independiente se reparte en una fase previa, el bloque presencial y una fase de cierre | Las sesiones largas permiten alternar bloques breves de exposición (máximo 30 min) con laboratorios, en una proporción cercana a mitad y mitad, y el bloque intensivo facilita la organización modular del programa. Las 32 h presenciales no cambian. El formulario conserva 16 semanas porque el formato oficial no admite menos (Anexo H) |
| Descripción | Dos frases generales, con errores de redacción ("Se explorar diferentes tecnicas") | Tres párrafos: propósito, relación con la IA actual y enfoque práctico | Una descripción precisa sirve de contrato con el estudiante y de referencia para el Consejo de Facultad |
| Número de unidades | 6 unidades | 7 unidades + proyecto integrador (8 sesiones) | Una unidad por sesión. Se añade una unidad nueva (razonamiento automático con solvers y en LLMs) y una de cierre (proyecto y hackatón) |
| Resultados de aprendizaje | No declarados | 8 resultados de aprendizaje, cada uno con unidades y evidencias (Anexo E) | Lo exige el Decreto 1330 de 2019. Además permiten verificar la alineación con los objetivos del Acuerdo 04 de 2025 |
| Metodología | No declarada; las actividades ("exposiciones", "taller evaluable", "presentación pública") aparecían mezcladas con los contenidos | Aula invertida; club de lectura como discusión; laboratorios en notebooks autocontenidos, que ocupan cerca de la mitad del tiempo presencial; trabajos independientes prácticos; contrapunto LLM y proyecto integrador conducido con un plan.md (Anexos A y J) | Separar contenidos de actividades da coherencia al formato. Los notebooks autocontenidos, con toda la explicación dentro del ejercicio, hacen viable la práctica con estudiantes de perfiles diversos |
| Evaluación | No declarada | Club de lectura 10 %, laboratorios y trabajos independientes 35 %, proyecto integrador 35 %, hackatón 20 %; sin quices ni exámenes escritos (Anexo D) | Evaluación continua y práctica, coherente con un posgrado de profundización. La hackatón reemplaza el examen y evalúa la competencia central en condiciones reales de tiempo. El club de lectura se evalúa por la participación en la discusión, no con quices |
| Prerrequisitos | Campo vacío | Declarado: sin prerrequisitos, con recomendaciones y material de nivelación | Deja explícito que la asignatura es accesible a profesionales no ingenieros |
| Bibliografía | 4 títulos: Meystel & Albus (2001), Hopgood (2021), Ramhorry (2024, BPB), Deckman (2024, edición Kindle) | 8 textos básicos de editoriales académicas (Pearson, CRC, Wiley, Cambridge, MIT Press, Springer), varios de acceso abierto, más lecturas por sesión de revistas y congresos de primer nivel | Ver la justificación de la bibliografía más abajo |
| Relación con otras asignaturas | Sin delimitar; duplicaba *Aprendizaje de Máquinas* y *Optimización e IA* | Fronteras explícitas con cada asignatura (Anexo F) | Evitar que los estudiantes cursen dos veces el mismo contenido |

### Comparación por unidad

| Unidad original (2024) | Unidad actual | Qué se conserva | Qué cambia | Justificación |
|---|---|---|---|---|
| **1. Inteligencia Artificial (IA), Sistemas Expertos (SE), IA Distribuida & Sistemas Multi-Agente (SMA)** | **U1**, con el mismo nombre | Generalidades e historia, solución de problemas, sistemas expertos, noción y arquitectura de agente, características, organización, cooperación, comunicación, coordinación y control de los SMA, metodologías GAIA y MAS-CommonKADS | Se añaden la representación del conocimiento (reglas, marcos, ontologías), el razonamiento basado en casos, el protocolo Contract Net, nociones de teoría de juegos para la coordinación y la evolución hacia SMA basados en LLMs. Las metodologías pasan a perspectiva histórica | Es la unidad fundacional y se conserva íntegra. Las metodologías de los años 2000 se mantienen como antecedente, pero la ingeniería de agentes actual se hace con frameworks basados en LLMs, que cubre *Agentes de IA (aplicado)* |
| **2. Planificación Automática en IA** | **U2**, con el mismo nombre | Generalidades, formalización de acciones, componentes, técnicas, planificación clásica y bajo incertidumbre (monitoreo y replanificación), caso de aplicación, composición de servicios | Se elimina la introducción a la IA y a los sistemas expertos, que repetía la unidad 1. La web semántica pasa a U1. Los temas clásicos se condensan: se añaden el lenguaje PDDL y la planificación jerárquica (HTN), y las técnicas de búsqueda se presentan como panorama. Se añaden la relación entre LLMs y planificación (LLM-Modulo) y los planes explícitos de los agentes basados en LLMs (plan.md), con una guía para escribirlos (Anexo J) | La repetición ocupaba tiempo sin aportar. PDDL es el estándar actual de la disciplina. La relación con los LLMs es hoy uno de los debates centrales de la IA (Kambhampati et ál., ICML 2024). El plan.md es la forma en que los agentes actuales hacen explícita su planificación. Enseñarlo junto a PDDL permite reconocer en él los conceptos clásicos de meta, descomposición, monitoreo y replanificación, y entender por qué necesita verificación |
| *(Web semántica, XML, RDF, ontologías, dentro de la unidad 2)* | Integrada en **U1** como representación del conocimiento | Ontologías y su sucesor actual, los grafos de conocimiento | Deja de ser un bloque propio. XML como formato de documentos web sale del temario | Las ontologías tienen sentido como forma de representar el conocimiento de un sistema experto, que es su lugar natural. El énfasis en XML y en la "visión de la web semántica" corresponde al estado de la técnica de los años 2000 |
| *(Nueva)* | **U3. Razonamiento Automático: Solvers, Restricciones y Razonamiento en LLMs** | — | Razonamiento simbólico (lógica, SAT/SMT, satisfacción de restricciones y verificación formal) y razonamiento en LLMs (cadena de pensamiento, autoconsistencia, árbol de pensamientos y modelos de razonamiento), contrastados sobre los mismos problemas | Ver "Contenidos nuevos" |
| **3. Visualización Científica (Visión por Computador)** | **U4**, con el mismo nombre | Introducción, percepción, procesamiento y análisis digital de imágenes, estudio de un problema | Se añaden el reconocimiento visual con modelos preentrenados y los modelos visión-lenguaje (CLIP, LLMs multimodales). El "estudio de un problema y presentación pública" pasa a los laboratorios. Se corrige el texto original (paréntesis sin cerrar) | La percepción es componente esencial de un sistema inteligente. La visión por computador está entre los objetivos específicos del programa (Acuerdo 04 de 2025, art. 2). Los modelos visión-lenguaje son hoy la forma predominante de reconocimiento visual |
| **4. Redes Neuronales, Algoritmos Evolutivos y Lógica Difusa** | **U5. Redes Neuronales y Aprendizaje Profundo (Deep Learning)** | Redes neuronales de propagación hacia adelante | Se amplían las redes neuronales a aprendizaje profundo, con una visión general de la arquitectura transformer. Se retiran los algoritmos evolutivos y la lógica difusa | Ver "Contenidos retirados" y "Contenidos nuevos" |
| **5. Aprendizaje de Máquina** | **U6**, con el mismo nombre | Generalidades, supervisado, no supervisado, refuerzo, exposición de algoritmos y casos de aplicación | Se diferencia de la asignatura obligatoria *Aprendizaje de Máquinas*. Se centra en el agente que aprende, los árboles de decisión y la inducción de reglas (puente con los sistemas expertos), los ensambles, la evaluación y la especificación de recompensas (*specification gaming*). La optimización estocástica pasa a U5 | Tal como estaba, la unidad duplicaba *Aprendizaje de Máquinas* (perceptrón, k-NN, k-means, Q-learning). Se conserva el tema, desde la perspectiva de los sistemas inteligentes: aprender el conocimiento que antes se codificaba a mano |
| **6. IA en Educación y Ambientes Colaborativos de Aprendizaje** | **U7. Razonamiento bajo Incertidumbre y Toma de Decisiones: aplicaciones en organizaciones y en educación** | Sistemas tutoriales inteligentes, ambientes colaborativos, SMA pedagógicos, planificación instruccional; el razonamiento basado en casos pasa a U1 | La IA en educación pasa de unidad completa a dominio de aplicación de una unidad de razonamiento probabilístico y decisión. Se añaden redes bayesianas, teoría de decisiones y valor de la información, y el modelo del estudiante (*Bayesian Knowledge Tracing*) y los tutores basados en LLMs | Los arts. 3 y 8 del Acuerdo 04 de 2025 prometen formación en "incertidumbre", y ninguna asignatura obligatoria la cubría. Los sistemas tutoriales inteligentes son un caso natural de razonamiento bajo incertidumbre, porque el modelo del estudiante es un modelo probabilístico. Así se conserva el tema y se amplía su aplicación a la formación corporativa, más cercana al perfil de la Facultad de Administración |
| *(Actividades: "exposiciones", "taller evaluable", "presentación pública")* | **U8. Proyecto integrador: sistemas inteligentes híbridos**, con hackatón | La intención de que el estudiante aplique y presente | Las actividades se formalizan como proyecto integrador sobre un problema real de la organización del estudiante y como hackatón final | Ver "Contenidos nuevos" |

### Contenidos retirados y por qué

- **Algoritmos evolutivos.** La asignatura obligatoria *Optimización e IA* ya cubre la computación evolutiva, PSO y colonias de hormigas como métodos de optimización. Mantenerlos aquí duplicaba contenido, y su tiempo se dedica al aprendizaje profundo, que ninguna obligatoria cubre.
- **Lógica difusa.** Tiene aplicaciones vigentes en control y evaluación, pero perdió peso en la práctica actual de la IA frente al aprendizaje profundo y al razonamiento probabilístico. Este último cumple su función de representar la incertidumbre y se cubre en U7. Con 8 sesiones, se priorizan los contenidos que el Acuerdo 04 de 2025 declara explícitamente.
- **Repetición de la introducción a la IA y a los sistemas expertos** en la unidad de planificación: se conserva una sola vez, en U1.
- **XML y la "visión de la web semántica"** como contenido propio: las ontologías se conservan dentro de U1.
- **Bibliografía de baja trazabilidad o desactualizada:**
  - Meystel & Albus (2001) fue superado por textos más recientes.
  - Deckman (2024) es una edición Kindle sin editorial académica.
  - Ramhorry (2024) es un manual de desarrollo de aplicaciones con IA generativa, cuyo contenido corresponde a *Agentes de IA* y *Procesamiento de Lenguaje Natural*.
  - Se conserva Hopgood (2021), el único texto del original que cubre el alcance clásico de los sistemas inteligentes.

### Contenidos nuevos y por qué

- **U3. Razonamiento automático: solvers, restricciones y razonamiento en LLMs.** La unidad estudia dos formas de razonar y las contrasta sobre los mismos problemas. Un solver es un motor que encuentra soluciones que cumplen todas las restricciones de un problema o demuestra que no existen. Un LLM razona generando pasos intermedios en lenguaje natural. La justificación tiene cuatro partes:
  - **Coincide con los cursos de referencia.** La satisfacción de restricciones y la lógica forman parte del núcleo común de los cursos de IA de referencia revisados (Berkeley CS188, Stanford CS221, CMU 15-281, Toronto CSC384, KU Leuven).
  - **Los LLMs actuales razonan de otra manera, y hay que entenderla.** La cadena de pensamiento (Wei et ál., NeurIPS 2022) y los modelos de razonamiento entrenados por refuerzo con recompensas verificables (DeepSeek-AI, *Nature* 2025) son hoy de uso generalizado. Un especialista debe saber qué hacen, cuánto cuestan y por qué una traza de razonamiento convincente no garantiza que la respuesta sea correcta ni que explique cómo se obtuvo (Turpin et ál., NeurIPS 2023).
  - **Es la base de los sistemas híbridos actuales.** La evidencia reciente muestra que los LLMs pierden exactitud en problemas combinatorios a medida que crece su complejidad (ZebraLogic, ICML 2025). Los sistemas más exitosos combinan un modelo de lenguaje que propone con un motor simbólico que verifica (AlphaGeometry, *Nature* 2024).
  - **Tiene aplicación organizacional directa** en horarios, turnos y verificación de cumplimiento normativo, y es la técnica que usa el reto 2 de la hackatón.
- **Planes explícitos en agentes basados en LLMs: plan.md (U2).** Los agentes actuales, como los asistentes de programación y los agentes de investigación, escriben su plan en un archivo de texto antes de actuar, lo someten a revisión humana y lo actualizan mientras ejecutan (Anthropic, 2025; Ji, 2025). Ese archivo reúne los conceptos clásicos de la unidad: meta, descomposición jerárquica, monitoreo y replanificación. A diferencia de un plan PDDL, no lo verifica un validador automático sino una persona y las pruebas que el propio plan declara. Por eso la unidad incluye una guía para escribirlo bien (Anexo J). El proyecto integrador la usa para su bitácora y la hackatón como punto de partida de cada equipo.
- **Aprendizaje profundo y arquitectura transformer (U5).** El art. 2 del Acuerdo 04 de 2025 declara como objetivo específico capacitar en "aprendizaje profundo". Además, el transformer es la arquitectura de los LLMs que el curso usa en cada sesión. Una visión general permite que el estudiante entienda qué hay detrás de esos modelos, sin invadir el estudio detallado que corresponde a las electivas propuestas de PLN y Aprendizaje Profundo.
- **Razonamiento bajo incertidumbre y teoría de decisiones (U7).** Cubre la "incertidumbre" que prometen los arts. 3 y 8 del Acuerdo 04 de 2025. Las redes bayesianas y la teoría de decisiones forman parte del núcleo común de los cursos de referencia.
- **Contrapunto LLM (transversal).** En las sesiones 2 a 7, al menos un laboratorio compara la técnica clásica con un LLM. Esto actualiza el programa sin renunciar a sus temas clásicos y forma criterio, con evidencia, sobre cuándo confiar en cada tipo de técnica.
- **IA responsable y regulación (U6 y U8).** El art. 2 del Acuerdo 04 de 2025 incluye como objetivo la formación en principios éticos e impactos sociales y legales de la IA. Se aborda con la especificación de objetivos (*specification gaming*), la verificación y la rendición de cuentas. También se estudian el Reglamento Europeo de IA y la Política Nacional de IA de Colombia (CONPES 4144 de 2025).
- **Proyecto integrador y hackatón (U8).** Convierten las "exposiciones" y el "taller evaluable" del original en evaluación auténtica: un problema real de la organización del estudiante, y la construcción en equipo de un sistema híbrido en tiempo limitado.

### Balance

De las seis unidades originales:
- **Cuatro se conservan con su nombre:** IA, SE, IAD & SMA; Planificación Automática; Visualización Científica; Aprendizaje de Máquina.
- **Una se conserva en su tema central, ampliado:** Redes Neuronales, que pasa a Aprendizaje Profundo.
- **Una se integra como aplicación:** IA en Educación, dentro de U7.

Se retiran dos subtemas (algoritmos evolutivos y lógica difusa) y se incorporan tres bloques nuevos (razonamiento automático con solvers y en LLMs, incertidumbre y decisión, proyecto integrador con hackatón), además de los planes explícitos para agentes (plan.md) dentro de la unidad de planificación. El resultado conserva la identidad del programa original, cumple la normativa de créditos, cubre los compromisos del Acuerdo 04 de 2025 y se diferencia de las demás asignaturas del plan.

---

## Nota de presentación

Este documento actualiza el contenido de *Sistemas Inteligentes* diligenciado el 25 de octubre de 2024. Conserva sus temáticas principales:
- IA, sistemas expertos y sistemas multiagente
- Planificación automática, extendida a los planes explícitos de los agentes basados en LLMs (plan.md)
- Web semántica (ontologías, como parte de la representación del conocimiento)
- Visión por computador
- Redes neuronales, ampliadas a aprendizaje profundo y a la arquitectura transformer
- Aprendizaje de máquina
- IA en educación

Corrige tres tipos de vacíos del programa original:
- **Contenidos repetidos:** la introducción a la IA aparecía dos veces.
- **Actividades listadas como contenidos:** exposiciones y talleres pasan a la metodología.
- **Componentes faltantes:** resultados de aprendizaje, metodología y evaluación. Además, la intensidad de 3,67 créditos se ajusta a los 4 que fija el Acuerdo 04 de 2025.

Cada temática se actualiza con un hilo conductor: el contraste entre las técnicas clásicas de los sistemas inteligentes y los modelos de lenguaje actuales (LLMs), y su integración en sistemas híbridos. La Unidad 3 (razonamiento automático: solvers, restricciones y razonamiento en LLMs) concentra ese hilo: contrasta cómo razonan los LLMs con los motores simbólicos que permiten verificar lo que proponen. La Unidad 2 lo lleva a los agentes con el plan.md, una forma explícita, revisable y verificable de planificar.

**Relación con *Agentes de IA (aplicado)*.** Sistemas Inteligentes cubre los fundamentos de agentes y sistemas multiagente: arquitectura, comunicación, coordinación y metodologías. *Agentes de IA* cubre la construcción práctica de agentes basados en LLMs con herramientas y frameworks.

---

# FORMATO PARA CREACIÓN DE UNA ASIGNATURA

**VICERRECTORÍA ACADÉMICA — UNIVERSIDAD NACIONAL DE COLOMBIA**

FECHA DE DILIGENCIAMIENTO: 21 | Octubre | 2026

---

## 1. IDENTIFICACIÓN DE LA ASIGNATURA

| Campo | Valor |
|---|---|
| 1.1. CÓDIGO DE LA ASIGNATURA | (Por asignar) |
| 1.2. NOMBRE DE LA ASIGNATURA | Sistemas Inteligentes |
| 1.3. SEDE | Manizales |
| 1.4. UNIDAD QUE OFRECE LA ASIGNATURA | Departamento de Informática y Computación |

## 2. DURACIÓN

| HAP | HAI | THS = HAP + HAI | No. de semanas | THP = THS × Semanas | No. de Créditos |
|---|---|---|---|---|---|
| 2 | 10 | 12 | 16 | 192 | 4 |

> **Intensidad horaria:** la actividad presencial (HAP × semanas = 32 h) se concentra en un bloque de **4 semanas, con 2 sesiones de 4 horas por semana** (8 sesiones). El formato oficial exige un periodo de entre 16 y 25 semanas, por lo que THS y semanas se diligencian sobre el periodo académico de 16 semanas y HAP = 2 es un promedio semanal. El trabajo independiente (160 h) se distribuye en una fase previa, el bloque presencial y una fase de cierre (Anexo A).
>
> Respecto al formato 2024, las HAI pasan de 9 a 10 para que THP/48 = 4 créditos, conforme al Acuerdo 04 de 2025 y al Decreto 1330 de 2019 (ver Anexo H).

## 3. VALIDABLE

Asignatura NO validable.

## 4. PORCENTAJE DE ASISTENCIA

80 % — Total de horas presenciales al semestre = HAP × Semanas = 32 — Mínimo de horas presenciales: 25,6

> Con sesiones de 4 horas, el estudiante puede faltar como máximo a **una** sesión: 7 sesiones suman 28 h, pero 6 sesiones suman 24 h, por debajo del mínimo.

## 5. REQUISITOS DE LA ASIGNATURA

| CÓDIGO | NOMBRE DE LA ASIGNATURA | TIPO DE REQUISITO |
|---|---|---|
| — | No requiere prerrequisitos. | — |

Se recomienda manejo básico de Python y nociones de probabilidad. La asignatura ofrece material de nivelación en ambos.

## 6. PLANES DE ESTUDIO A LOS QUE SE ASOCIA LA ASIGNATURA

| CÓDIGO | NOMBRE DEL PLAN DE ESTUDIOS | COMPONENTE | AGRUPACIÓN | OBLIGATORIA / OPTATIVA |
|---|---|---|---|---|
| | Especialización en Inteligencia Artificial | | | Obligatoria |

## 7. ASIGNATURA DE LIBRE ELECCIÓN

No.

---

# PROGRAMA DE LA ASIGNATURA

## 8. DESCRIPCIÓN DE LA ASIGNATURA

La asignatura busca que los estudiantes adquieran competencias en el diseño, la implementación y el análisis de sistemas que razonan, aprenden y actúan de manera autónoma, y en la identificación y aplicación de estas técnicas en problemas del mundo real. Recorre las principales familias de técnicas de los sistemas inteligentes:
- Sistemas expertos y sistemas multiagente
- Planificación automática, incluidos los planes explícitos de los agentes basados en LLMs
- Razonamiento automático con solvers y razonamiento en LLMs
- Visión por computador
- Redes neuronales y aprendizaje profundo, incluida la arquitectura transformer
- Aprendizaje de máquina
- Razonamiento bajo incertidumbre, con aplicaciones en organizaciones y en educación

Cada familia de técnicas se estudia en diálogo con la IA actual. La asignatura analiza, con evidencia empírica reciente, qué pueden y qué no pueden hacer los modelos de lenguaje de gran escala (LLMs) frente a las técnicas clásicas. Estudia también cómo razonan y planifican los propios LLMs (cadenas de pensamiento, modelos de razonamiento y planes explícitos de los agentes) y por qué sus resultados requieren verificación. Finalmente, estudia cómo integrarlos en sistemas híbridos (neurosimbólicos), en los que el modelo de lenguaje aporta flexibilidad y las técnicas clásicas aportan corrección, verificación y explicabilidad.

El enfoque es práctico y de modelado aplicado. El curso se organiza en 8 sesiones presenciales de 4 horas, concentradas en 4 semanas (dos sesiones por semana). En cada sesión se discute una lectura académica y se alternan bloques breves de exposición con laboratorios prácticos, que ocupan cerca de la mitad del tiempo. A lo largo del curso los estudiantes desarrollan un proyecto integrador sobre un problema real de su organización. El curso cierra con una hackatón en la que construyen, en equipo y en tiempo limitado, un sistema inteligente híbrido para un reto organizacional. La evaluación es práctica: no hay quices ni exámenes escritos.

## 9. CONTENIDO

### 9.1. CONTENIDO BÁSICO — 9.2. CONTENIDO DETALLADO

**Unidad 1. Inteligencia Artificial (IA), Sistemas Expertos (SE), IA Distribuida & Sistemas Multi-Agente (SMA)** (sesión 1)
- Generalidades e historia de la IA: las olas simbólica, conexionista y neurosimbólica; áreas de investigación y aplicación
- Solución de problemas complejos utilizando técnicas de IA: formulación de problemas y búsqueda heurística (panorama)
- Sistemas expertos: representación del conocimiento (reglas, marcos y ontologías; de la web semántica a los grafos de conocimiento), base de conocimiento, motor de inferencia (encadenamiento hacia adelante y hacia atrás), módulo de explicación y adquisición del conocimiento; razonamiento basado en casos (RBC); los sistemas expertos hoy (reglas de negocio, tablas de decisión) y los LLMs como fuente de conocimiento
- Inteligencia Artificial Distribuida y noción de agente: especificación PEAS y arquitectura interna (reactiva, deliberativa, BDI e híbrida)
- Sistemas multiagente: características, arquitecturas, organización social, cooperación, comunicación (lenguajes y protocolos de interacción, *Contract Net*), coordinación y control; nociones de teoría de juegos para la coordinación (equilibrio, subastas, votación)
- Metodologías de diseño y desarrollo de SMA (GAIA, MAS-CommonKADS) y su evolución hacia los sistemas multiagente basados en LLMs (panorama)

**Unidad 2. Planificación Automática en IA** (sesión 2)
- Generalidades y formalización: acciones con precondiciones y efectos (STRIPS, lenguaje PDDL); componentes de un sistema de planificación (modelo del dominio, planificador, validador y ejecutor)
- Técnicas de planificación (panorama): planificación clásica como búsqueda heurística, planificación jerárquica (HTN) y ejecución con monitoreo y replanificación ante resultados inesperados; casos de aplicación: composición de servicios y de procesos de negocio, y misiones espaciales (Deep Space 1, rovers de Marte)
- LLMs y planificación: evidencia empírica (PlanBench, modelos de razonamiento y la posición contrastante de 2026), el marco LLM-Modulo (generar y verificar) y el LLM como traductor de lenguaje natural a PDDL
- Planes explícitos en agentes basados en LLMs (plan.md): el plan como artefacto en lenguaje natural que una persona revisa y aprueba antes de la ejecución; correspondencias con la planificación clásica (meta y criterios de aceptación, descomposición jerárquica, monitoreo con la lista de pasos y replanificación); el plan como memoria externa del agente; plan.md frente a plan PDDL, es decir, verificación humana frente a verificación automática
- Cómo escribir un plan.md correcto: explorar antes de planificar; estructura (objetivo verificable, contexto, alcance y exclusiones, restricciones, pasos con dependencias y verificación, criterios de aceptación, riesgos y puntos de aprobación humana, registro de avance); principios y errores frecuentes (Anexo J)

**Unidad 3. Razonamiento Automático: Solvers, Restricciones y Razonamiento en LLMs** (sesión 3)
- Razonamiento simbólico: lógica y restricciones como lenguajes de modelado (satisfacibilidad SAT/SMT, problemas de satisfacción de restricciones y programación con restricciones con CP-SAT)
- Verificación formal con solvers: comprobar reglas, políticas y planes, con contraejemplos como explicación; aplicaciones organizacionales (horarios y turnos, asignación de recursos, cumplimiento normativo)
- Cómo razonan los LLMs: cadena de pensamiento (*chain-of-thought*), autoconsistencia (varias cadenas y voto por mayoría) y árbol de pensamientos (búsqueda sobre razonamientos parciales, en conexión con la búsqueda heurística de U1)
- Modelos de razonamiento: más cómputo en el momento de la inferencia y entrenamiento por refuerzo con recompensas verificables (se retoma en U6); costo en tokens y latencia; las trazas de razonamiento no son necesariamente explicaciones fieles
- Razonamiento simbólico frente a razonamiento en LLMs: pérdida de exactitud a medida que crece la complejidad combinatoria; el LLM como formalizador y el solver como verificador; sistemas neurosimbólicos de referencia (AlphaGeometry)

**Unidad 4. Visualización Científica (Visión por Computador)** (sesión 4)
- Introducción y percepción: del sensor al percepto en un sistema inteligente
- Formación y representación de imágenes digitales
- Visión artificial, procesamiento digital de imágenes: histogramas, filtrado, detección de bordes, umbralización y morfología
- Visión artificial, análisis digital de imágenes: segmentación, extracción de características, medición y visualización de resultados
- Reconocimiento visual: del pipeline clásico a las redes convolucionales y los modelos fundacionales visión-lenguaje (CLIP, LLMs multimodales), a nivel de uso
- Estudio de un problema de aplicación organizacional: inspección de calidad, conteo, análisis de documentos

**Unidad 5. Redes Neuronales y Aprendizaje Profundo (Deep Learning)** (sesión 5)
- De la neurona artificial al perceptrón multicapa: capas, funciones de activación y propagación hacia adelante
- Entrenamiento de redes neuronales: función de pérdida, retropropagación y descenso de gradiente estocástico (aprendizaje como optimización estocástica, a nivel conceptual); sobreajuste y regularización (dropout, parada temprana)
- Aprendizaje profundo: representaciones jerárquicas, el papel de los datos y del cómputo (GPU) y panorama de arquitecturas (convolucionales para imágenes, recurrentes para secuencias y transformers)
- Arquitectura transformer (visión general): tokenización y embeddings; mecanismo de atención y autoatención; atención multicabeza; codificación posicional; bloques codificador y decodificador; variantes solo codificador (BERT), solo decodificador (GPT) y codificador-decodificador
- De los transformers a los modelos fundacionales y los LLMs: preentrenamiento, escala y ajuste por instrucciones (panorama); capacidades, límites y lugar de las redes profundas en los sistemas inteligentes híbridos

**Unidad 6. Aprendizaje de Máquina** (sesión 6)
- Generalidades del aprendizaje de máquina: el agente que aprende (elemento de desempeño, crítico, generador de problemas) y tipos de aprendizaje
- Aprendizaje supervisado: árboles de decisión e inducción de reglas, es decir, el aprendizaje automático de la base de conocimiento de un sistema experto; ensambles; evaluación y validación (sobreajuste, validación cruzada y métricas según el costo del error)
- Aprendizaje no supervisado como descubrimiento de estructura (panorama)
- Aprendizaje por refuerzo: procesos de decisión de Markov, políticas y recompensas; solución con modelo (iteración de valores) y aprendizaje por interacción; el refuerzo con recompensas verificables en los modelos de razonamiento (panorama, retoma U3)
- Especificación de objetivos: recompensas mal especificadas y *specification gaming*
- Exposición de algoritmos y casos de aplicación

**Unidad 7. Razonamiento bajo Incertidumbre y Toma de Decisiones: aplicaciones en organizaciones y en educación** (sesión 7)
- Fuentes de incertidumbre; probabilidad como grado de creencia; regla de Bayes y falacia de la tasa base
- Redes bayesianas: representación, independencia condicional e inferencia; redes dinámicas y modelos ocultos de Markov (panorama)
- Teoría de decisiones: utilidad esperada, redes de decisión (diagramas de influencia) y valor de la información
- De la correlación a la causalidad (panorama)
- IA en educación y ambientes colaborativos de aprendizaje: sistemas tutoriales inteligentes (modelos del dominio, del estudiante y pedagógico), planificación instruccional, sistemas multiagente pedagógicos y tutores basados en LLMs; aplicación a la formación corporativa

**Unidad 8. Proyecto integrador: sistemas inteligentes híbridos** (transversal; cierre en la sesión 8)
- IA neurosimbólica: taxonomía de integraciones y el patrón generar-verificar
- Razonamiento y planificación en LLMs, síntesis crítica: qué muestra y qué no muestra la evidencia sobre los modelos de razonamiento (retoma U2 y U3)
- IA responsable en sistemas autónomos: verificación, trazabilidad y rendición de cuentas; marco regulatorio (Reglamento (UE) 2024/1689 y CONPES 4144 de 2025)
- Proyecto integrador sobre un problema real de la organización del estudiante
- Hackatón: construcción en equipo de un sistema inteligente híbrido en tiempo limitado

## 10. BIBLIOGRAFÍA BÁSICA

| AUTOR (ES) | TÍTULO | EDITORIAL - PAÍS | AÑO |
|---|---|---|---|
| Stuart J. Russell, Peter Norvig | Artificial Intelligence: A Modern Approach (4.ª edición) | Pearson — EE. UU. | 2021 |
| Adrian A. Hopgood | Intelligent Systems for Engineers and Scientists: A Practical Guide to Artificial Intelligence (4.ª edición) | CRC Press — EE. UU. | 2021 |
| Michael Wooldridge | An Introduction to MultiAgent Systems (2.ª edición) | John Wiley & Sons — Reino Unido | 2009 |
| Malik Ghallab, Dana Nau, Paolo Traverso | Acting, Planning, and Learning | Cambridge University Press — Reino Unido | 2025 |
| David L. Poole, Alan K. Mackworth | Artificial Intelligence: Foundations of Computational Agents (3.ª edición; texto completo abierto en artint.info) | Cambridge University Press — Reino Unido | 2023 |
| Richard Szeliski | Computer Vision: Algorithms and Applications (2.ª edición; PDF para uso personal en szeliski.org/Book) | Springer — Suiza | 2022 |
| Simon J. D. Prince | Understanding Deep Learning (PDF gratuito oficial en udlbook.github.io/udlbook) | MIT Press — EE. UU. | 2023 |
| Mykel J. Kochenderfer, Tim A. Wheeler, Kyle H. Wray | Algorithms for Decision Making (PDF abierto oficial en algorithmsbook.com) | MIT Press — EE. UU. | 2022 |

## 11. NOMBRE DEL DIRECTOR ACADÉMICO

(Por diligenciar)

## 12. APROBACIÓN DEL CONSEJO DE FACULTAD

(Por diligenciar)

Elaboró: Ernesto Cuartas Morales — ecuartasmo@unal.edu.co

---
---

# ANEXOS

## Anexo A. Estructura de la sesión de 4 horas y distribución del trabajo independiente

**Estructura de referencia de las sesiones 3 a 7 (la misma de la sesión 2)**

Cada sesión alterna bloques breves de exposición con laboratorios, en una proporción cercana a mitad y mitad: unos 115 minutos de exposición y discusión, y unos 110 de práctica. Ningún bloque de exposición supera 30 minutos. Cada bloque termina con su síntesis, el anuncio del trabajo independiente y la transición a su laboratorio. Las sesiones 1 y 8 tienen estructura propia (Anexo B); la sesión 2 usa esta estructura con un tercer laboratorio de la unidad (2C) en el lugar del laboratorio de proyecto.

| Inicio | Actividad | Tipo | Duración |
|---|---|---|---|
| 0:00 | Club de lectura: discusión guiada de las tesis y la evidencia de la lectura | Discusión | 20 min |
| 0:20 | Bloque 1: conceptos clave de la unidad, con ejemplos organizacionales | Exposición | 30 min |
| 0:50 | Laboratorio A: técnica clásica aplicada a un caso organizacional | Práctica | 35 min |
| 1:25 | Bloque 2: segunda parte de la unidad | Exposición | 20 min |
| 1:45 | Laboratorio B: segunda aplicación o contrapunto LLM, midiendo validez, costo y explicabilidad | Práctica | 35 min |
| 2:20 | Pausa | — | 15 min |
| 2:35 | Bloque 3: aplicaciones y relación con los LLMs | Exposición | 30 min |
| 3:05 | Laboratorio de proyecto: cada equipo aplica la técnica de la sesión a su caso y actualiza el plan.md del proyecto (Anexo J) | Práctica | 40 min |
| 3:45 | Cierre: síntesis, trabajos independientes y lectura de la sesión siguiente | Exposición | 15 min |

**Calendario del bloque presencial (4 semanas, 2 sesiones de 4 h por semana)**

| Semana | Primera sesión de la semana | Segunda sesión de la semana |
|---|---|---|
| 1 | Sesión 1 — U1: IA, SE, IAD & SMA | Sesión 2 — U2: Planificación Automática en IA |
| 2 | Sesión 3 — U3: Razonamiento Automático: Solvers, Restricciones y Razonamiento en LLMs | Sesión 4 — U4: Visualización Científica (Visión por Computador) |
| 3 | Sesión 5 — U5: Redes Neuronales y Aprendizaje Profundo | Sesión 6 — U6: Aprendizaje de Máquina |
| 4 | Sesión 7 — U7: Razonamiento bajo Incertidumbre y Toma de Decisiones | Sesión 8 — U8: Proyecto integrador y hackatón |

**Distribución del trabajo independiente (160 h)**

Las 192 h de trabajo que corresponden a 4 créditos no caben en 4 semanas: serían 48 h semanales. Por eso el trabajo independiente se distribuye en tres fases dentro del periodo académico.

| Fase | Duración | Actividades | Horas aprox. |
|---|---|---|---|
| Fase previa | 2 semanas antes de la sesión 1 | Nivelación en Python y probabilidad; instalación y verificación del entorno (VS Code, Python 3.13 y las extensiones de Python y Jupyter; Anexo G.1) y acceso al LLM; lecturas y capítulos de apoyo de la semana 1; identificación de un caso organizacional candidato para el proyecto | 24 |
| Bloque presencial | 4 semanas | Cada semana: lecturas y capítulos de apoyo de las dos sesiones de la semana siguiente (≈ 4 h), trabajos independientes de las dos sesiones de la semana (≈ 7 h), terminar y entregar los laboratorios de la semana (≈ 8 h) y avance del proyecto integrador (≈ 5 h) | 96 (≈ 24 por semana) |
| Fase de cierre | 2 semanas después de la sesión 8 | Informe final y prototipo del proyecto integrador; entrega de los laboratorios de la semana 4; reflexión individual de la hackatón | 40 |
| **Total** | | | **160** |

Durante el bloque presencial la carga es de unas 32 h por semana (8 h presenciales y 24 h independientes). Conviene advertirlo a los estudiantes antes de iniciar.

**Principios metodológicos**
- **Mitad exposición, mitad práctica.** Los bloques de exposición duran como máximo 30 minutos y se alternan con laboratorios. Las diapositivas no incluyen actividades interactivas planeadas: la interacción se da de forma natural, sobre todo en el club de lectura y en los laboratorios.
- **Modelar antes que programar.** Los laboratorios son notebooks autocontenidos: toda la explicación está dentro del ejercicio y el andamiaje de código viene preparado, de modo que el estudiante se concentra en formular el problema, usar la técnica e interpretar los resultados. Esto los hace accesibles para perfiles no ingenieriles. Se inician en clase y se terminan como trabajo independiente.
- **Aula invertida.** Con bloques de exposición breves, la lectura y el capítulo de apoyo previos son indispensables. El club de lectura es una discusión guiada, sin quices: la preparación se nota en la calidad de la discusión. Como las dos sesiones de una semana pueden ser en días consecutivos, las dos lecturas de cada semana se asignan al cierre de la semana anterior; las de la semana 1, en la fase previa.
- **Contrapunto LLM.** En las sesiones 2 a 7, al menos un laboratorio compara la técnica clásica con un LLM. Los resultados se acumulan en una tabla común que se analiza en la sesión 8.
- **Caso organizacional.** El proyecto integrador avanza en cada sesión mediante su plan.md (en el cierre de las sesiones 1 y 2 y en el laboratorio de proyecto de las sesiones 3 a 7), que hace de bitácora: se marcan los pasos cumplidos, se registran las desviaciones y se replanifica de forma explícita (Anexo J).
- **Evaluación práctica.** No hay quices ni exámenes escritos en ninguna sesión. Se evalúan los laboratorios, los trabajos independientes, el proyecto integrador, la hackatón y la participación en el club de lectura (Anexo D).
- **IA generativa.** Se permite como herramienta de consulta en laboratorios, trabajos independientes, proyecto y hackatón, declarando su uso.
- **Requisito logístico.** El entorno por defecto de los laboratorios es VS Code, en el computador de cada estudiante (Anexo G.1). Cada estudiante lo instala en la fase previa y lo comprueba con un notebook de verificación antes de la sesión 1. También antes de la sesión 1 debe definirse el acceso de los estudiantes a un LLM vía API (cuenta institucional o nivel gratuito de un proveedor), con un presupuesto por estudiante; los laboratorios con LLM pueden usar, además, un modelo local. Para la sesión 3 el acceso debe incluir un modelo de razonamiento, y para la sesión 4 un LLM multimodal, que acepte imágenes. El laboratorio de la sesión 1 (curso Claude 101 de Anthropic) requiere que cada estudiante cree una cuenta gratuita en la plataforma de cursos de Anthropic. Para la sesión 2, el planificador y el validador de planes también pueden usarse sin instalación en el editor en línea editor.planning.domains.

## Anexo B. Plan de sesiones

### Sesión 1 — Unidad 1: IA, Sistemas Expertos, IA Distribuida & Sistemas Multi-Agente (semana 1, primera sesión)

- **Lectura (fase previa):** Garcez, A. d'Avila, Lamb, L. C. (2023). *Neurosymbolic AI: The 3rd Wave*. Artificial Intelligence Review 56(11), 12387–12406. https://arxiv.org/abs/2012.05876 (recorre la historia simbólica y conexionista de la IA y el lugar de los sistemas expertos).
- **Apoyo del texto guía:** Russell & Norvig (AIMA), cap. 1–2; Hopgood, capítulos de sistemas basados en reglas y de RBC; Wooldridge, capítulos introductorios.
- **Estructura de la sesión.** Es la sesión introductoria y tiene estructura propia: la charla inicial y los tres bloques de exposición dejan menos tiempo de práctica que el resto del curso. El balance de mitad exposición y mitad práctica rige desde la sesión 2.

| Inicio | Actividad | Tipo | Duración |
|---|---|---|---|
| 0:00 | Charla inicial: «Quiero ser parte del mundo del AI: ¿cómo lo logro? y ¿cómo sobrevivo a él?» | Exposición | 45 min |
| 0:45 | Discusión tipo seminario | Discusión | 15 min |
| 1:00 | Bloque 1: IA y sistemas expertos (incluye el encadenamiento hacia adelante y hacia atrás trazado paso a paso) | Exposición | 60 min |
| 2:00 | Pausa | — | 15 min |
| 2:15 | Bloque 2: IA distribuida y agentes | Exposición | 30 min |
| 2:45 | Bloque 3: sistemas multiagente (incluye Contract Net paso a paso) | Exposición | 30 min |
| 3:15 | Laboratorio: curso Claude 101 de Anthropic | Práctica | 30 min |
| 3:45 | Cierre: mapa de la unidad, arranque del proyecto integrador y trabajos | Exposición | 15 min |

- **Laboratorio — Claude 101.** Curso gratuito de Anthropic sobre el uso de Claude en el trabajo diario: conversaciones, proyectos, artefactos, skills, conectores e investigación. https://anthropic.skilljar.com/claude-101. Se inicia en clase y se completa como trabajo independiente; la evidencia es el certificado del curso.
- **Trabajo independiente** (3 h 45 min; entrega al inicio de la semana 2):
  - **TI-1 · Su propio sistema experto en papel (75 min).** Entre 6 y 8 reglas de una decisión de su organización, trazas de encadenamiento hacia adelante y hacia atrás, y la explicación que daría a un auditor. Recoge el propósito del antiguo laboratorio de sistemas expertos.
  - **TI-2 · Un agente para su organización (60 min).** PEAS, clasificación del entorno y arquitectura recomendada. Es insumo de la propuesta del proyecto integrador.
  - **TI-3 · ¿Cuándo conviene un sistema multiagente con LLMs? (90 min).** Lectura del blog de Anthropic sobre su sistema de investigación multiagente (2025) y de la figura 1 y la sección 4 de Cemri et al. (NeurIPS 2025), con preguntas guía sobre roles, protocolos, coordinación y verificación.
- **Proyecto integrador (en el cierre):** conformación de equipos, selección del caso organizacional (a partir del caso candidato identificado en la fase previa) y descripción PEAS del caso.

### Sesión 2 — Unidad 2: Planificación Automática en IA (semana 1, segunda sesión)

- **Lectura (club de lectura):** Kambhampati, S. et ál. (2024). *Position: LLMs Can't Plan, But Can Help Planning in LLM-Modulo Frameworks*. ICML 2024. https://proceedings.mlr.press/v235/kambhampati24a.html
- **Apoyo del texto guía:** AIMA, cap. 11 («Automated Planning»); Ghallab, Nau & Traverso (capítulos seleccionados); guía del plan.md (Anexo J).
- **Estructura de la sesión.** Tres pares de exposición y laboratorio: unos 115 minutos de exposición y discusión, y 110 de práctica.

| Inicio | Actividad | Tipo | Duración |
|---|---|---|---|
| 0:00 | Club de lectura: ¿pueden planificar los LLMs? | Discusión | 20 min |
| 0:20 | Bloque 1: planificación automática clásica | Exposición | 30 min |
| 0:50 | Laboratorio 2A | Práctica | 35 min |
| 1:25 | Bloque 2: LLMs y planificación | Exposición | 20 min |
| 1:45 | Laboratorio 2B | Práctica | 35 min |
| 2:20 | Pausa | — | 15 min |
| 2:35 | Bloque 3: planes explícitos en agentes (plan.md) | Exposición | 30 min |
| 3:05 | Laboratorio 2C | Práctica | 40 min |
| 3:45 | Cierre: síntesis, proyecto integrador, trabajos y lectura de la sesión 3 | Exposición | 15 min |

- **Caso hilo.** La misma orden de MantenIA (restablecer la bomba 3 de la Planta Norte) recorre los tres bloques:
  - en el bloque 1, como plan en PDDL trazado estado por estado;
  - en el bloque 2, como plan propuesto por un LLM con un error que el validador detecta;
  - en el bloque 3, como plan.md de la intervención, con una replanificación.
- **Laboratorio 2A — Planificar una operación en PDDL.** Formalizar en PDDL una orden de mantenimiento de MantenIA, resolverla con Unified Planning y Fast Downward, validar el plan y analizar cómo cambia al modificar metas y recursos. Extensión opcional: el mismo procedimiento como red jerárquica de tareas (HTN).
- **Laboratorio 2B — LLM-Modulo en práctica.** Sobre las mismas instancias se comparan tres estrategias:
  1. El LLM planifica directamente.
  2. El LLM traduce el problema a PDDL y lo resuelve un planificador.
  3. Un ciclo generar-verificar en el que el validador devuelve los errores al LLM.

  Se miden la validez de los planes, las iteraciones y el costo.
- **Laboratorio 2C — Escribir, revisar y ejecutar un plan.md.**
  1. Un LLM redacta el plan.md de una intervención de MantenIA con la estructura del Anexo J.
  2. El equipo lo revisa con la lista de chequeo (J.6), lo corrige y lo aprueba.
  3. En la ejecución simulada se inyecta una falla. El equipo la registra en el plan.md, replanifica y vuelve a aprobar.

  Al cierre se discute qué errores detectó la revisión humana y cuáles habría detectado un validador.
- **Trabajo independiente** (3 h 30 min; entrega al inicio de la semana 2):
  - **TI-1 · Su proceso como problema de planificación (70 min).** 3–4 acciones de un proceso de su organización con precondiciones y efectos, un plan trazado a mano y una regla de negocio convertida en precondición.
  - **TI-2 · Ponga a prueba a un LLM como planificador (65 min).** Verificar a mano el plan de un LLM para el problema del TI-1, repetir con nombres ofuscados y, opcionalmente, validar con VAL en el editor en línea.
  - **TI-3 · El plan.md de una tarea real de su trabajo (75 min).** Pedir el plan.md a un LLM, revisarlo con la lista de chequeo (J.6) y documentar al menos cinco correcciones.
- **Proyecto integrador.** La **propuesta** se entrega al inicio de la sesión: problema, organización, decisión a apoyar, datos disponibles y técnicas candidatas. En el cierre, cada equipo empieza el **plan.md del proyecto** con la plantilla de la sesión; la primera versión se entrega al inicio de la semana 2.

### Sesión 3 — Unidad 3: Razonamiento Automático: Solvers, Restricciones y Razonamiento en LLMs (semana 2, primera sesión)

- **Lectura:** Trinh, T. H., Wu, Y., Le, Q. V., He, H., Luong, T. (2024). *Solving olympiad geometry without human demonstrations* (AlphaGeometry). Nature 625, 476–482. https://www.nature.com/articles/s41586-023-06747-5. Es un sistema neurosimbólico en el que un modelo de lenguaje propone y un motor de deducción simbólica demuestra.
- **Apoyo del texto guía:** AIMA, cap. 6 y 7; Poole & Mackworth, capítulos de restricciones y de proposiciones e inferencia. Para el razonamiento en LLMs, Wei et ál. (2022) y DeepSeek-AI (2025) (Anexo G.2).
- **Laboratorio 3A — Programación de turnos: CP-SAT frente al razonamiento de los LLMs.** Modelar la asignación de turnos de personal: cobertura mínima, descansos, competencias, preferencias y equidad. Diagnosticar la infactibilidad cuando las restricciones entran en conflicto y analizar el efecto de relajarlas. Contrapunto: sobre instancias de tamaño creciente se comparan cuatro formas de razonar con un LLM, y el modelo de restricciones verifica todas las respuestas:
  1. El LLM responde directamente.
  2. El mismo LLM con cadena de pensamiento.
  3. Varias muestras del LLM, eligiendo por voto (autoconsistencia) o con el verificador (generar-verificar).
  4. Un modelo de razonamiento.

  Se registran la validez, los tokens consumidos (incluidos los de razonamiento), el costo y el tamaño de instancia a partir del cual cada estrategia deja de producir soluciones válidas.
- **Laboratorio 3B — Verificación de políticas de negocio con Z3.** Codificar un reglamento interno (por ejemplo, políticas de aprobación de descuentos o créditos) como fórmulas lógicas y detectar contradicciones, lagunas y casos no cubiertos, usando los contraejemplos como explicación. Contrapunto: un LLM traduce la política de lenguaje natural a Z3 y el solver verifica; se compara con un LLM que razona directamente sobre los mismos casos con cadena de pensamiento. Su traza se contrasta con el contraejemplo del solver: ¿es correcta la explicación del LLM cuando su respuesta lo es? Extensión: verificar con Z3 que la base de reglas del sistema experto del trabajo independiente 1 de la sesión 1 es consistente.
- **Laboratorio de proyecto:** identificar las restricciones y reglas del caso que deben garantizarse, cómo se verificarían y qué partes del razonamiento podrían delegarse a un LLM con verificación; actualizar el plan.md.

### Sesión 4 — Unidad 4: Visualización Científica (Visión por Computador) (semana 2, segunda sesión)

- **Lectura:** Radford, A. et ál. (2021). *Learning Transferable Visual Models From Natural Language Supervision* (CLIP). ICML 2021, PMLR 139, 8748–8763. https://proceedings.mlr.press/v139/radford21a/radford21a.pdf (se asignan la introducción, el enfoque y la discusión de limitaciones).
- **Apoyo del texto guía:** Szeliski, capítulos de introducción, procesamiento de imágenes y reconocimiento; AIMA, cap. 25.
- **Laboratorio 4A — Procesamiento y análisis digital de imágenes.** Con OpenCV y scikit-image, construir un pipeline clásico para un problema de inspección: detectar y medir defectos en productos o contar objetos en imágenes de una operación. Incluye histograma, filtrado, umbralización, morfología, segmentación, medición y visualización de los resultados intermedios.
- **Laboratorio 4B — Reconocimiento con modelos preentrenados.** Sobre un conjunto etiquetado del caso, comparar la clasificación *zero-shot* con CLIP frente a un LLM multimodal. Se reportan la matriz de confusión, el costo por imagen y el análisis de errores, y se discute cuándo basta el pipeline clásico del laboratorio 4A.
- **Laboratorio de proyecto:** identificar si el caso tiene un componente perceptual (imágenes, documentos escaneados, sensores).

### Sesión 5 — Unidad 5: Redes Neuronales y Aprendizaje Profundo (Deep Learning) (semana 3, primera sesión)

- **Lectura (blog de referencia en IA):** Alammar, J. (2018, 27 de junio). *The Illustrated Transformer*. https://jalammar.github.io/illustrated-transformer/ (explicación visual de la arquitectura propuesta en *Attention Is All You Need*; se lee junto con las figuras del artículo original).
- **Apoyo del texto guía:** Prince, *Understanding Deep Learning*, capítulos de redes superficiales y profundas, entrenamiento y transformers; AIMA, cap. 21.
- **Laboratorio 5A — Del perceptrón a la red profunda.** Con PyTorch, construir y entrenar un perceptrón multicapa para un problema de clasificación de negocio (por ejemplo, abandono de clientes). Observar la retropropagación con diferenciación automática, interpretar las curvas de aprendizaje, provocar sobreajuste y corregirlo con regularización (dropout, parada temprana). Comparar redes de distinta profundidad y anchura.
- **Laboratorio 5B — El transformer por dentro.** Implementar la atención por producto punto escalado sobre una oración corta y visualizar sus pesos. Después, con un transformer preentrenado pequeño (por ejemplo, GPT-2 vía Hugging Face):
  - Explorar la tokenización y los embeddings.
  - Inspeccionar los pesos de atención de sus capas.
  - Generar texto variando la temperatura.

  Contrapunto: comparar sus respuestas con las de un LLM actual en las mismas tareas, para discutir qué cambia con la escala y el ajuste por instrucciones y qué se mantiene de la arquitectura.
- **Laboratorio de proyecto:** entrega del **avance** (modelo del caso con al menos una técnica del curso y resultados preliminares).

### Sesión 6 — Unidad 6: Aprendizaje de Máquina (semana 3, segunda sesión)

- **Lectura (blog de referencia en IA):** Krakovna, V. et ál. (2020, 21 de abril). *Specification gaming: the flip side of AI ingenuity*. Google DeepMind Blog. https://deepmind.google/discover/blog/specification-gaming-the-flip-side-of-ai-ingenuity/
- **Apoyo del texto guía:** AIMA, cap. 19 y 22; Kochenderfer et ál., capítulos "Exact Solution Methods" y de aprendizaje por refuerzo.
- **Laboratorio 6A — Del dato al conocimiento.** Inducir un árbol de decisión a partir de datos históricos de una decisión organizacional y extraer sus reglas. Compararlo con la base de reglas del sistema experto de la sesión 1 (trabajo independiente 1) y con un modelo de ensamble en exactitud, interpretabilidad y costo del error, con validación cruzada.
- **Laboratorio 6B — Aprendizaje por refuerzo y *specification gaming*.** Modelar un problema de inventario o de mantenimiento como proceso de decisión de Markov. Resolverlo con iteración de valores (modelo conocido) y con un agente que aprende por interacción, y comparar las políticas. Después, modificar la recompensa con un indicador aparentemente razonable y observar cómo el agente "cumple la métrica sin cumplir el objetivo".
- **Laboratorio de proyecto:** analizar riesgos de automatizar la decisión del caso y la supervisión que requiere.

### Sesión 7 — Unidad 7: Razonamiento bajo Incertidumbre y Toma de Decisiones (semana 4, primera sesión)

- **Lectura:** Pearl, J. (2019). *The Seven Tools of Causal Inference, with Reflections on Machine Learning*. Communications of the ACM 62(3), 54–60. https://doi.org/10.1145/3241036
- **Apoyo del texto guía:** AIMA, cap. 12, 13 y 16; Kochenderfer et ál., capítulos de razonamiento probabilístico y "Simple Decisions".
- **Laboratorio 7A — Red bayesiana y decisión con valor de la información.** Con pyAgrum, construir una red bayesiana para un problema de riesgo organizacional (abandono de clientes o falla de equipos), con consultas diagnósticas y predictivas. Extenderla a un diagrama de influencia que calcule la decisión óptima y cuánto vale obtener información adicional antes de decidir.
- **Laboratorio 7B — Sistema tutorial inteligente: modelo del estudiante.** Implementar el modelo *Bayesian Knowledge Tracing* (un modelo oculto de Markov) para estimar el dominio de una habilidad a partir de secuencias de respuestas, y diseñar la regla de selección del siguiente ejercicio (planificación instruccional). Aplicación a la formación corporativa. Contrapunto: un tutor basado en LLM estima el dominio a partir de las mismas respuestas; se compara con el modelo bayesiano.
- **Laboratorio de proyecto:** cierre técnico; se definen el componente híbrido y la demostración final.

### Sesión 8 — Unidad 8: Proyecto integrador y hackatón (semana 4, segunda sesión)

- **Lectura:** Shojaee, P. et ál. (2025). *The Illusion of Thinking: Understanding the Strengths and Limitations of Reasoning Models via the Lens of Problem Complexity*. NeurIPS 2025. https://arxiv.org/abs/2506.06941 — con la réplica de Lawsen, A. (2025). *Comment on The Illusion of Thinking*. https://arxiv.org/abs/2506.09250 (se leen en par para discutir por qué verificar).
- **Estructura de la sesión:**

| Bloque | Duración | Actividad |
|---|---|---|
| Apertura | 10 min | Síntesis de la lectura y de la tabla de contrapunto LLM del semestre; presentación del reto |
| Muestra de proyectos integradores | 50 min | Pitch de cada equipo (5 min + 2 min de preguntas) |
| — Pausa | 10 min | |
| Reto 1 de la hackatón (laboratorio 8A) | 70 min | Modelado y solución del caso con técnicas del curso |
| Reto 2 de la hackatón (laboratorio 8B) | 70 min | Componente híbrido LLM + técnica clásica con verificación |
| Demostraciones y cierre | 30 min | Demostración de 3 min por equipo, deliberación del jurado y premiación |

- El detalle de la hackatón está en el Anexo C.

## Anexo C. Hackatón

**Propósito.** Reemplaza el examen individual. Evalúa, en condiciones de tiempo limitado, la competencia central del curso: elegir la técnica adecuada para un problema nuevo, resolverlo con herramientas profesionales e integrarla con un LLM de forma verificable.

**Equipos.** De tres personas, conformados al azar el día de la sesión y distintos de los equipos del proyecto integrador, para mezclar perfiles.

**El reto.** Un caso organizacional que se revela al inicio de la sesión y admite varias técnicas del curso (sistema experto, planificación, modelo de restricciones o lógica con solver, visión, red neuronal o modelo preentrenado, modelo de aprendizaje, red bayesiana). El docente prepara dos o tres casos y elige uno. Ejemplos:
- Programar las sesiones de un evento académico de la Facultad.
- Inspeccionar y priorizar solicitudes de mantenimiento a partir de fotografías y reportes.
- Decidir sobre un portafolio de proyectos con información incierta.

**Desarrollo:**
- **Plan del equipo (primeros 10 min del reto 1):** cada equipo escribe un plan.md breve con la estructura del Anexo J y lo actualiza al cerrar cada reto.
- **Reto 1 (70 min):** resolver el caso con la técnica o combinación de técnicas que el equipo considere más adecuada, justificar la elección y declarar sus garantías y limitaciones. Entregable: cuaderno ejecutable, plan.md y una diapositiva.
- **Reto 2 (70 min):** añadir un componente híbrido. Un LLM recibe una solicitud en lenguaje natural (por ejemplo, un cambio de requisitos de último minuto o una imagen nueva), la traduce a la representación de la técnica clásica, la técnica la resuelve y un verificador comprueba el resultado. La demostración debe incluir al menos un caso en el que el verificador detecte un error del LLM.
- **Demostración (3 min por equipo)** ante un jurado conformado por el docente y, preferiblemente, un invitado del sector productivo.

**Rúbrica:**

| Criterio | Peso |
|---|---|
| Corrección del modelo y de la solución | 30 % |
| Elección y justificación de la técnica, plan.md del equipo y declaración de garantías y limitaciones | 20 % |
| Componente híbrido y calidad de la verificación | 25 % |
| Claridad de la demostración ante una audiencia directiva | 15 % |
| Reproducibilidad del cuaderno | 10 % |

**Componente individual.** Cada estudiante entrega, en las 48 horas siguientes, una reflexión de una página: su aporte al equipo, qué decisión de diseño cambiaría y qué aprendió del contraste entre el LLM y la técnica clásica.

**Logística:**
- Cuaderno base para VS Code, con todas las librerías del curso instaladas y probadas en el entorno del curso.
- Credenciales de acceso al LLM con presupuesto asignado.
- Datos del caso preparados.
- Se permite cualquier herramienta, declarando su uso.

## Anexo D. Evaluación

| Componente | Peso | Modalidad | Momento |
|---|---|---|---|
| Club de lectura y discusiones: participación | 10 % | Individual | Sesiones 1–8 (en la sesión 1, la discusión tipo seminario) |
| Laboratorios y trabajos independientes | 35 % | Laboratorios en parejas; trabajos independientes individuales | Los de cada semana se entregan al inicio de la semana siguiente; los de la semana 4, en la fase de cierre |
| · Laboratorios (14): el curso Claude 101 en la sesión 1, tres en la sesión 2 (2A, 2B y 2C) y dos por sesión en las sesiones 3 a 7 | | | |
| · Trabajos independientes de cada sesión (prácticos, con criterios de evaluación propios) | | | |
| Proyecto integrador | 35 % | Equipo (2–3) | |
| · Propuesta y primera versión del plan.md | 5 % | | Propuesta: sesión 2 (semana 1). Plan.md: inicio de la semana 2 |
| · Avance, con el plan.md actualizado | 10 % | | Sesión 5 (semana 3) |
| · Pitch en la muestra de proyectos | 5 % | | Sesión 8 (semana 4) |
| · Informe final y prototipo | 15 % | | Fase de cierre (hasta 2 semanas después de la sesión 8) |
| Hackatón | 20 % | | Sesión 8 (semana 4) |
| · Retos y demostración (rúbrica del Anexo C) | 15 % | Equipo (3) | |
| · Reflexión individual | 5 % | Individual | 48 h después |

**No hay quices ni exámenes escritos** en ninguna sesión. Toda la evaluación es práctica, y la hackatón reemplaza el examen individual. El docente fija en el programa-calendario la proporción entre laboratorios y trabajos independientes dentro del 35 %.

Los "talleres evaluables", "exposiciones" y "presentación pública" del programa original quedan incorporados en los laboratorios, la muestra de proyectos y la hackatón.

## Anexo E. Resultados de aprendizaje

| Código | Resultado de aprendizaje | Unidades | Evidencia |
|---|---|---|---|
| RA1 | Caracterizar un problema organizacional como sistema agente-entorno y seleccionar la técnica de IA adecuada, justificando sus garantías y limitaciones | 1, 8 | Proyecto, hackatón |
| RA2 | Diseñar sistemas basados en conocimiento (sistemas expertos, razonamiento basado en casos, representación del conocimiento) | 1, 6 | Trabajo independiente 1 de la sesión 1 (sistema experto), Lab 6A |
| RA3 | Diseñar sistemas multiagente con mecanismos de comunicación, cooperación y coordinación | 1 | Trabajos independientes 2 y 3 de la sesión 1 |
| RA4 | Modelar y resolver problemas de planificación, restricciones y lógica con planificadores y solvers, verificar formalmente la validez de las soluciones y especificar planes explícitos y verificables (plan.md) para agentes basados en LLMs | 2, 3, 8 | Labs 2A, 2B, 2C, 3A, 3B; plan.md del proyecto |
| RA5 | Construir soluciones de percepción visual combinando procesamiento clásico de imágenes y modelos preentrenados | 4 | Labs 4A, 4B |
| RA6 | Explicar y aplicar redes neuronales y aprendizaje profundo, incluida la arquitectura transformer, y técnicas de aprendizaje de máquina | 5, 6 | Labs 5A, 5B, 6A, 6B |
| RA7 | Razonar y decidir bajo incertidumbre con modelos probabilísticos y de decisión, en contextos organizacionales y educativos | 7 | Labs 7A, 7B |
| RA8 | Diseñar y evaluar críticamente sistemas híbridos LLM + técnicas clásicas, eligiendo entre las estrategias de razonamiento de los LLMs y los solvers según su validez, su costo y la fidelidad de sus explicaciones, y analizar sus riesgos éticos, de responsabilidad y regulatorios | 1–8 | Labs de contrapunto (en particular 2B, 3A y 3B), Lab 6B, hackatón |

**Alineación con el Acuerdo 04 de 2025:**
- **Art. 2, objetivo general:** RA1 y RA4–RA7.
- **Art. 2, objetivos específicos:**
  - Aprendizaje automático, aprendizaje profundo y visión por computadora: RA5 y RA6.
  - Ética: RA8.
- **Arts. 3 y 8:**
  - Sistemas basados en conocimiento: RA2.
  - Optimización e incertidumbre: RA6 y RA7.

## Anexo F. Fronteras con las demás asignaturas

Esta versión recupera temas del programa original que también tocan otras asignaturas. Para evitar duplicación, se fija un tratamiento diferenciado. Conviene validarlo en una reunión con los docentes de *Aprendizaje de Máquinas* y *Optimización e IA*.

| Tema | Otra asignatura | Tratamiento en Sistemas Inteligentes |
|---|---|---|
| Aprendizaje de máquina | Aprendizaje de Máquinas (programa 2024: perceptrón, k-NN, reglas de asociación, Apriori, k-means, agrupamiento jerárquico, Q-learning) | SI no repite esos algoritmos. Se centra en el agente que aprende, los árboles de decisión y la inducción de reglas (puente con los sistemas expertos), los ensambles, la evaluación y la especificación de recompensas. Superposición aceptada: generalidades y concepto de aprendizaje por refuerzo |
| Redes neuronales y aprendizaje profundo | Aprendizaje de Máquinas (perceptrón); Aprendizaje Profundo e IA Generativa (electiva propuesta) | SI ofrece una visión general en una sesión: perceptrón multicapa, entrenamiento, regularización y panorama de arquitecturas, al nivel necesario para usar redes profundas dentro de sistemas inteligentes. El estudio detallado de arquitecturas, entrenamiento con GPU, transfer learning y modelos generativos queda en la electiva |
| Optimización combinatoria y programación matemática | Optimización e IA | SI usa CP-SAT y SMT para modelar restricciones lógicas y de factibilidad y para verificar soluciones. No cubre programación lineal/entera ni metaheurísticas |
| Algoritmos evolutivos | Optimización e IA (computación evolutiva, PSO, colonias de hormigas) | No se cubre en SI |
| Visión por computador | Aprendizaje Profundo e IA Generativa (electiva propuesta) | SI cubre la percepción como componente de un sistema inteligente: procesamiento y análisis clásico de imágenes y uso de modelos preentrenados. El diseño y entrenamiento de redes convolucionales y transformers de visión queda en la electiva |
| Construcción de agentes LLM (herramientas, MCP, memoria, frameworks, guardrails) | Agentes de IA (aplicado) | SI cubre los fundamentos (arquitectura de agente, comunicación, coordinación, metodologías de SMA). La construcción con frameworks LLM queda en Agentes |
| Planes explícitos para agentes (plan.md) | Agentes de IA (aplicado) | SI enseña el plan.md como artefacto de planificación: su relación con la planificación clásica, cómo escribirlo bien y cómo verificarlo. La construcción de agentes que lo generan y lo ejecutan (patrones *plan-and-execute* y ReAct, memoria, herramientas y frameworks) queda en Agentes |
| Razonamiento en LLMs (cadena de pensamiento, autoconsistencia, modelos de razonamiento) | Procesamiento de Lenguaje Natural; Agentes de IA (aplicado) | SI estudia estas estrategias como formas de razonamiento y las contrasta con los solvers en validez, costo y fidelidad. El prompting como técnica general (ejemplos, plantillas, optimización de prompts) queda en PLN |
| Transformers, prompting, RAG, fine-tuning | Procesamiento de Lenguaje Natural | SI presenta una visión general de la arquitectura transformer (atención, variantes codificador/decodificador) como fundamento conceptual. El estudio detallado de los modelos de lenguaje, el prompting, RAG y fine-tuning quedan en PLN. En los laboratorios los LLMs se usan vía API; solo en U3 se comparan sus estrategias de razonamiento |
| Interfaces y usabilidad | Interacción Humano Computador | No se cubre |

## Anexo G. Entorno de laboratorio y lecturas complementarias

### G.1 Librerías por laboratorio

**Entorno por defecto: VS Code.** Cada estudiante trabaja en su propio computador con VS Code, las extensiones de Python y Jupyter, Python 3.13 y un entorno virtual del curso. Lo instala en la fase previa con una guía paso a paso y lo comprueba con un notebook de verificación. Las librerías principales de la tabla publican paquetes para Python 3.13 en Windows, macOS y Linux, con una excepción: `torch` no los publica para Mac con procesador Intel (verificado el 21-oct-2026). Los laboratorios con LLM funcionan con una clave de API o con un modelo local, por ejemplo servido con Ollama. Se recomienda fijar versiones en cada cuaderno y probar el entorno completo antes de la sesión 1 y de la hackatón.

**Respaldo: Google Colab.** Para quien no pueda instalar software, y para los laboratorios con `torch` en un Mac con procesador Intel. Su entorno usa Python 3.13 desde el 19 de agosto de 2026. En Colab no está disponible la opción de modelo local, y los archivos de apoyo de cada laboratorio deben subirse junto con el notebook.

| Laboratorio | Librerías | Observaciones |
|---|---|---|
| 1 (Claude 101) | Navegador; cuenta gratuita en la plataforma de cursos de Anthropic | Curso en línea: se inicia en clase y se completa como trabajo independiente |
| 2A | `unified-planning==1.3.0`, `up-fast-downward==1.0.0`; la parte HTN (opcional) usa un expansor incluido en el laboratorio | Fijar la versión de UPF e instalar los motores uno a uno. Instalar `up-fast-downward` por separado: el extra `unified-planning[fast-downward]` instala la versión antigua 0.5.2 (probado el 21-oct-2026 con la 1.0.0, que integra Fast Downward 26.6). Validar siempre los planes HTN: en una prueba se obtuvo un plan inválido. Alternativa sin instalación: editor.planning.domains (botón «Solver», con VAL) |
| 2B | `unified-planning==1.3.0` (validador incluido) y `up-fast-downward==1.0.0`; API de un LLM, o un modelo local con Ollama (`qwen3:4b-instruct`); sin ninguno de los dos, respuestas grabadas | Registrar la validez, las iteraciones y el costo de cada estrategia |
| 2C | API de un LLM, o un modelo local con Ollama (`qwen3:4b-instruct`); sin ninguno de los dos, respuestas grabadas; plantilla del plan.md (Anexo J) | Opcional: redactar el plan.md con el modo de planificación de un agente de programación (por ejemplo, Claude Code) |
| 3A | `ortools` (9.15, CP-SAT); API de un LLM con acceso a un modelo de razonamiento | Registrar los tokens de razonamiento que reporta la API para calcular el costo. Fijar el número de muestras de la autoconsistencia según el presupuesto |
| 3B | `z3-solver`; API de un LLM | Estable y activo |
| 4A | `opencv-python`, `scikit-image` | Verificar su instalación en el entorno del curso |
| 4B | `transformers` y `torch` (modelo CLIP preentrenado); API de un LLM multimodal | En CPU, con un lote pequeño de imágenes; para un lote grande conviene una GPU (por ejemplo, en Colab) |
| 5A | `torch` | Una red pequeña sobre datos tabulares se entrena en CPU; la GPU es opcional |
| 5B | `torch`, `transformers` (modelo preentrenado pequeño, por ejemplo GPT-2); API de un LLM | Los pesos de atención se obtienen del modelo y se visualizan con matplotlib |
| 6A | `scikit-learn` | Árboles, extracción de reglas, ensambles y validación cruzada |
| 6B | `numpy` (iteración de valores y agente de aprendizaje implementados en el cuaderno); opcional `gymnasium` | |
| 7A | `pyagrum` (3.2) | Redes bayesianas y diagramas de influencia en una sola librería |
| 7B | `numpy` (Bayesian Knowledge Tracing implementado en el cuaderno); API de un LLM | |
| Hackatón | Todas las anteriores en un cuaderno base | Probar el cuaderno base completo en el entorno del curso (VS Code) la semana anterior, y también en Colab como respaldo |

### G.2 Lecturas complementarias por sesión (opcionales)

- **Sesión 1:**
  - Akata, E. et ál. (2025). *Playing Repeated Games with Large Language Models*. Nature Human Behaviour 9. https://arxiv.org/abs/2305.16867
  - Hogan, A. et ál. (2021). *Knowledge Graphs*. ACM Computing Surveys 54(4). https://arxiv.org/abs/2003.02320 (para la representación del conocimiento con ontologías)
- **Sesión 2:**
  - Valmeekam, K. et ál. (2023). *PlanBench*. NeurIPS 2023. https://arxiv.org/abs/2206.10498
  - Valmeekam, K., Stechly, K., Kambhampati, S. (2024). *LLMs Still Can't Plan; Can LRMs? A Preliminary Evaluation of OpenAI's o1 on PlanBench*. https://arxiv.org/abs/2409.13373
  - Valmeekam, K., Stechly, K., Gundawar, A., Kambhampati, S. (2025). *A Systematic Evaluation of the Planning and Scheduling Abilities of the Reasoning Model o1*. TMLR. https://arxiv.org/abs/2410.02162
  - Corrêa, A. B., Pereira, A. G., Seipp, J. (2026). *Frontier Large Language Models Are Becoming Competitive with State-of-the-Art Planners*. Communications of the ACM (en prensa). Preprint: https://arxiv.org/abs/2511.09378 (posición contrastante)
  - Tantakoun, M., Muise, C., Zhu, X. (2025). *LLMs as Planning Formalizers: A Survey for Leveraging Large Language Models to Construct Automated Planning Models*. Findings of ACL 2025, 25167–25188. https://aclanthology.org/2025.findings-acl.1291/
  - NASA (2026, 30 de enero). *NASA's Perseverance Rover Completes First AI-Planned Drive on Mars*. https://www.nasa.gov/missions/mars-2020-perseverance/perseverance-rover/nasas-perseverance-rover-completes-first-ai-planned-drive-on-mars/ (un plan generado por IA y verificado en un gemelo digital antes de ejecutarse)
  - Wang, L. et ál. (2023). *Plan-and-Solve Prompting: Improving Zero-Shot Chain-of-Thought Reasoning by Large Language Models*. ACL 2023. https://arxiv.org/abs/2305.04091 (pedir al LLM que primero planifique y después ejecute)
  - Anthropic (2025, 29 de septiembre). *Effective context engineering for AI agents*. https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents (el plan y las notas como memoria externa del agente)
  - Ji, Y. (2025, 18 de julio). *Context Engineering for AI Agents: Lessons from Building Manus*. https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus (el archivo todo.md como forma de mantener presentes los objetivos)
- **Sesión 3:**
  - Solvers y razonamiento simbólico:
    - Lin, B. Y. et ál. (2025). *ZebraLogic: On the Scaling Limits of LLMs for Logical Reasoning*. ICML 2025. https://proceedings.mlr.press/v267/lin25i.html
    - Pan, L. et ál. (2023). *Logic-LM: Empowering Large Language Models with Symbolic Solvers for Faithful Logical Reasoning*. Findings of EMNLP 2023. https://arxiv.org/abs/2305.12295
  - Razonamiento en LLMs:
    - Wei, J. et ál. (2022). *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*. NeurIPS 2022. https://arxiv.org/abs/2201.11903
    - Wang, X. et ál. (2023). *Self-Consistency Improves Chain of Thought Reasoning in Language Models*. ICLR 2023. https://arxiv.org/abs/2203.11171
    - Yao, S. et ál. (2023). *Tree of Thoughts: Deliberate Problem Solving with Large Language Models*. NeurIPS 2023. https://arxiv.org/abs/2305.10601
    - DeepSeek-AI (2025). *DeepSeek-R1 incentivizes reasoning in LLMs through reinforcement learning*. Nature 645, 633–638. https://arxiv.org/abs/2501.12948
    - Snell, C. et ál. (2024). *Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters*. arXiv. https://arxiv.org/abs/2408.03314
    - Turpin, M. et ál. (2023). *Language Models Don't Always Say What They Think: Unfaithful Explanations in Chain-of-Thought Prompting*. NeurIPS 2023. https://arxiv.org/abs/2305.04388
- **Sesión 4:** Szeliski (2022), capítulos de segmentación y reconocimiento.
- **Sesión 5:**
  - Vaswani, A. et ál. (2017). *Attention Is All You Need*. NeurIPS 2017. https://arxiv.org/abs/1706.03762 (artículo original de la arquitectura transformer)
  - LeCun, Y., Bengio, Y., Hinton, G. (2015). *Deep learning*. Nature 521, 436–444. https://www.nature.com/articles/nature14539 (revisión de referencia sobre el aprendizaje profundo)
- **Sesión 6:** Yue, Y. et ál. (2025). *Does Reinforcement Learning Really Incentivize Reasoning Capacity in LLMs Beyond the Base Model?* NeurIPS 2025. https://proceedings.neurips.cc/paper_files/paper/2025/hash/537d5aa768c2d534016a4d06f87bc8fb-Abstract-Conference.html
- **Sesión 7:**
  - Corbett, A. T., Anderson, J. R. (1994). *Knowledge tracing: Modeling the acquisition of procedural knowledge*. User Modeling and User-Adapted Interaction 4, 253–278. https://link.springer.com/article/10.1007/BF01099821
  - Kıcıman, E. et ál. (2024). *Causal Reasoning and Large Language Models*. TMLR. https://mlanthology.org/tmlr/2024/kiciman2024tmlr-causal/
- **Sesión 8:**
  - Kambhampati, S. et ál. (2026). *Position: Stop Anthropomorphizing Intermediate Tokens as Reasoning/Thinking Traces!* ICML 2026. https://arxiv.org/abs/2504.09762
  - Departamento Nacional de Planeación (2025). *Documento CONPES 4144: Política Nacional de Inteligencia Artificial*. https://colaboracion.dnp.gov.co/CDT/Conpes/Econ%C3%B3micos/4144.pdf

### G.3 Bibliografía complementaria

| Autor(es) | Título | Editorial — País | Año |
|---|---|---|---|
| Aidan Hogan et ál. | Knowledge Graphs (versión HTML abierta en kgbook.org) | Morgan & Claypool — EE. UU. | 2021 |
| Yoav Shoham, Kevin Leyton-Brown | Multiagent Systems: Algorithmic, Game-Theoretic, and Logical Foundations | Cambridge University Press — Reino Unido | 2009 |
| Patrik Haslum, Nir Lipovetzky, Daniele Magazzeni, Christian Muise | An Introduction to the Planning Domain Definition Language | Morgan & Claypool — EE. UU. | 2019 |
| Aston Zhang, Zachary C. Lipton, Mu Li, Alexander J. Smola | Dive into Deep Learning (libro interactivo con código, abierto en d2l.ai) | Cambridge University Press — Reino Unido | 2023 |
| Uffe B. Kjærulff, Anders L. Madsen | Bayesian Networks and Influence Diagrams (2.ª ed.) | Springer — EE. UU. | 2013 |
| Judea Pearl, Madelyn Glymour, Nicholas P. Jewell | Causal Inference in Statistics: A Primer | John Wiley & Sons — Reino Unido | 2016 |
| Judea Pearl, Dana Mackenzie | El libro del porqué: la nueva ciencia de la causa y el efecto (divulgación, en español) | Pasado y Presente — España | 2020 |
| Pascal Hitzler et ál. (eds.) | Handbook on Neurosymbolic AI and Knowledge Graphs | IOS Press — Países Bajos | 2025 |
| Andrea Aler Tubella, Virginia Dignum et ál. | Trustworthy AI: Ethical Frameworks for Responsible Innovation | Cambridge University Press — Reino Unido | 2026 |

Como apoyo en español para los capítulos introductorios, de búsqueda y de lógica puede usarse la 2.ª edición en español de Russell & Norvig (Pearson Educación, 2004).

## Anexo H. Nota normativa

- **Créditos:** un crédito equivale a 48 horas de trabajo del estudiante (Acuerdo 033 de 2007 del CSU, art. 6). Los créditos se expresan en números enteros (Decreto 1330 de 2019, art. 2.5.3.2.4.2). Con 2 HAP + 10 HAI × 16 semanas = 192 h, la asignatura tiene exactamente los 4 créditos que fija el Acuerdo 04 de 2025.
- **Bloque presencial de 4 semanas:**
  - **Por qué el formulario dice 16 semanas.** El formato de asignaturas de posgrado de la DNPP establece que "en ningún caso el número de semanas podrá ser inferior a 16, ni superior a 25". Por eso el formulario se diligencia con 16 semanas y HAP = 2 como promedio semanal.
  - **Dónde se fija el bloque.** La concentración de las 32 h presenciales en 4 semanas (2 sesiones de 4 h por semana) se establece en el programa-calendario de la asignatura, que el Acuerdo 008 de 2008 del CSU (art. 23) asigna al profesor.
  - **Respaldo normativo.** El Acuerdo 033 de 2007 deja el número de horas presenciales a "la asignatura y la metodología empleada". No se encontró norma que obligue a distribuirlas de manera uniforme, y otros posgrados de la Facultad en la sede ya operan con sesiones concentradas. Conviene confirmar este esquema con la Dirección Académica de la sede.
- **Carga de trabajo:** 4 créditos equivalen a 192 h de trabajo del estudiante. Si todo ese trabajo tuviera que ocurrir dentro de las 4 semanas presenciales, la carga sería de 48 h semanales, lo que no es realista para estudiantes que trabajan. Por eso el trabajo independiente se extiende a una fase previa y una fase de cierre dentro del periodo académico (Anexo A). Si el programa exigiera completar todo el trabajo en las 4 semanas, la carga real dejaría de corresponder a 4 créditos.
- **Asistencia:** con un mínimo de 25,6 h, faltar a dos sesiones (8 h) implica perder la asignatura. Debe advertirse en la sesión 1.
- **Otras asignaturas:** la inconsistencia de 2 HAP + 9 HAI (3,67 créditos) también está en las otras tres obligatorias y en *Agentes de IA (aplicado)*. Conviene corregirlas en el mismo trámite.

## Anexo I. Trazabilidad con el programa original (2024)

| Unidad o tema del programa 2024 | Decisión en esta versión | Dónde queda |
|---|---|---|
| **IA, SE, IAD & SMA**: generalidades e historia, solución de problemas complejos, áreas de investigación y aplicación, sistemas expertos | Conservado y actualizado | U1 (mismo nombre), con RBC y sistemas expertos actuales |
| IAD, noción de agente (arquitectura interna), SMA: características, arquitecturas, organización social, cooperación, comunicación, coordinación, control | Conservado y actualizado | U1, con Contract Net, nociones de teoría de juegos y SMA basados en LLMs |
| Metodologías MAS-CommonKADS y GAIA | Conservado como panorama | U1, en perspectiva histórica y con su evolución |
| Exposiciones sobre tópicos en IAD y SMA | Reubicado | Charla inicial y discusión tipo seminario de la sesión 1, club de lectura y trabajo independiente 3 de la sesión 1 |
| **Planificación Automática en IA**: generalidades, formalización de acciones, componentes, técnicas, planificación clásica y bajo incertidumbre, caso de aplicación | Conservado, condensado y actualizado | U2 (mismo nombre), con PDDL, HTN y LLM-Modulo; las técnicas se presentan como panorama para dar espacio al plan.md |
| Composición de servicios web | Conservado como caso | U2: composición de servicios y procesos de negocio como problema de planificación |
| Web semántica, XML, RDF, lenguajes de ontologías | Reducido | U1: ontologías y grafos de conocimiento como formas de representación del conocimiento. Deja de ser unidad para dar espacio al razonamiento automático (U3) |
| Introducción a la IA y sistemas expertos dentro de "Planificación" (repetido) | Eliminada la repetición | Solo en U1 |
| **Visualización Científica (Visión por Computador)**: introducción, percepción, procesamiento y análisis digital de imágenes, estudio de un problema | Conservado y actualizado | U4 (mismo nombre), con modelos visión-lenguaje |
| **Redes Neuronales, Algoritmos Evolutivos y Lógica Difusa** | Redes neuronales: conservadas y ampliadas. Algoritmos evolutivos y lógica difusa: retirados | U5: Redes Neuronales y Aprendizaje Profundo (Deep Learning), con visión general de la arquitectura transformer. Los algoritmos evolutivos se estudian en *Optimización e IA* |
| **Aprendizaje de Máquina**: generalidades, supervisado, no supervisado, optimización estocástica, refuerzo, casos de aplicación | Conservado, diferenciado de la asignatura *Aprendizaje de Máquinas* | U6 (mismo nombre); la optimización estocástica se ve en U5 |
| **IA en Educación y Ambientes Colaborativos de Aprendizaje**: STI, ACA, SMA pedagógicos, planificación instruccional, RBC | Conservado como aplicación | U7 (sistemas tutoriales inteligentes y laboratorio 7B); RBC en U1 |
| "Taller evaluable", "Estudio de un problema y presentación pública" | Reubicado | Laboratorios, muestra de proyectos y hackatón |
| Bibliografía 2024 | Se conserva Hopgood (actualizado a la 4.ª ed., 2021); se reemplazan Meystel & Albus (2001) y los títulos autopublicados | Sección 10 |
| *(Nuevo)* Razonamiento automático, restricciones y verificación con solvers | Añadido | U3: es la base de la verificación en los sistemas híbridos y la que usa la hackatón |
| *(Nuevo)* Razonamiento en LLMs: cadena de pensamiento, autoconsistencia, árbol de pensamientos y modelos de razonamiento | Añadido | U3 y laboratorios 3A y 3B; refuerzo con recompensas verificables en U6; síntesis crítica en U8 |
| *(Nuevo)* Planes explícitos en agentes basados en LLMs (plan.md) | Añadido | U2 y laboratorio 2C; guía en el Anexo J; el plan.md del proyecto integrador reemplaza la bitácora; punto de partida de la hackatón |
| *(Nuevo)* Razonamiento bajo incertidumbre y teoría de decisiones | Añadido | U7: cubre la "incertidumbre" que declaran los arts. 3 y 8 del Acuerdo 04 de 2025 |
| *(Nuevo)* Contrapunto LLM y sistemas híbridos | Añadido | Hilo transversal y U8 |

## Anexo J. Guía: cómo escribir un plan.md correcto

Un **plan.md** es un archivo de texto en formato Markdown donde un agente basado en LLM, o una persona junto con el agente, escribe el plan de una tarea antes de ejecutarla y lo mantiene actualizado mientras la ejecuta. El nombre varía según la herramienta, pero la función es la misma. Según su documentación oficial: el modo de planificación de Claude Code, el archivo `.plan.md` de Cursor, el `tasks.md` de Kiro, los archivos `plan.md` y `tasks.md` de GitHub Spec Kit, el `PLANS.md` que propone OpenAI para Codex y el `todo.md` de Manus (ver fuentes). La guía aplica tanto al plan que redacta el agente como al que una persona escribe para que el agente lo ejecute.

**Para qué sirve**
1. **Contrato revisable.** Una persona lo lee, lo corrige y lo aprueba antes de que el agente actúe. Es el momento más barato para detectar que el agente entendió mal la tarea.
2. **Memoria externa.** El plan vive fuera de la ventana de contexto del modelo. Si la tarea es larga o se retoma en otra sesión, el agente recupera el estado leyendo el archivo (Anthropic, 2025).
3. **Monitoreo.** Las casillas marcadas y el registro de avance muestran qué se hizo, qué falló y qué cambió. Al reescribir su lista de pendientes, el agente vuelve a poner los objetivos al final del contexto y reduce el riesgo de desviarse de ellos (Ji, 2025).

### J.1 Relación con la planificación clásica (U2)

| Elemento del plan.md | Concepto de planificación clásica |
|---|---|
| Objetivo y criterios de aceptación | Meta (condiciones del estado objetivo) |
| Contexto y supuestos | Estado inicial |
| Pasos con dependencias | Acciones con precondiciones y efectos; orden parcial |
| Fases y subtareas | Descomposición jerárquica (HTN) |
| Casillas y registro de avance | Monitoreo de la ejecución |
| Actualización del plan ante una falla | Replanificación |
| Revisión y aprobación humana | Validación del plan |

La diferencia central está en la verificación. Un plan PDDL se valida de forma automática contra un modelo formal del dominio. Un plan.md lo valida una persona y, paso a paso, las verificaciones que el propio plan declara. Por eso la calidad de un plan.md depende, sobre todo, de que cada paso tenga una verificación que se pueda ejecutar.

### J.2 Cuándo conviene

- **Conviene** cuando el enfoque no es obvio, cuando la tarea toca varias partes (archivos, sistemas o áreas de la organización) o cuando el dominio es poco conocido.
- **No conviene** para tareas que se describen en una frase. La guía de buenas prácticas de Claude Code lo resume así: si el cambio cabe en una frase, se omite el plan (Anthropic, s. f.).

### J.3 Proceso en cinco pasos

1. **Explorar sin actuar.** El agente lee el contexto (documentos, datos, código) y responde preguntas, sin modificar nada. Los asistentes de programación ofrecen un modo de planificación que impone esta separación.
2. **Redactar el plan** con la estructura de J.4.
3. **Revisar y aprobar.** La persona revisa el plan con la lista de chequeo de J.6 y lo corrige antes de autorizar la ejecución.
4. **Ejecutar con verificación.** El agente ejecuta paso a paso, corre la verificación de cada paso y marca la casilla solo cuando la verificación pasa.
5. **Mantenerlo vivo y cerrar.** Ante una falla o un hallazgo, el plan se actualiza de forma explícita (qué cambió y por qué), en lugar de improvisar. Al terminar, el resultado se comprueba contra los criterios de aceptación.

### J.4 Estructura recomendada

| Sección | Qué contiene | Pregunta que responde |
|---|---|---|
| 1. Objetivo | El resultado esperado, en una o dos frases verificables | ¿Qué existirá o habrá cambiado al terminar? |
| 2. Contexto | Estado actual; fuentes, sistemas, archivos y datos involucrados; supuestos | ¿De dónde partimos? |
| 3. Alcance | Qué incluye y, de forma explícita, qué queda fuera | ¿Qué no se debe tocar? |
| 4. Restricciones | Normas, plazos, presupuesto, herramientas permitidas, datos sensibles | ¿Qué límites no se negocian? |
| 5. Pasos | Lista numerada con casillas. Cada paso: una acción, su resultado esperado, sus dependencias y su verificación | ¿Qué se hace, en qué orden y cómo se sabe que quedó bien? |
| 6. Criterios de aceptación | Una verificación de extremo a extremo que demuestra que el objetivo se cumplió | ¿Cómo se comprueba el resultado completo? |
| 7. Riesgos y aprobaciones | Riesgos con su señal de alerta y su respuesta; pasos que requieren aprobación humana | ¿Dónde debe decidir una persona? |
| 8. Registro de avance | Bitácora con fecha y hora: pasos cumplidos, desviaciones, replanificaciones y decisiones | ¿Qué pasó y qué cambió? |

### J.5 Principios

1. **Objetivo verificable.** "Arreglar la bomba 3 lo antes posible" no es verificable. "Bomba 3 en servicio hoy antes de las 14:00, con el sello cambiado y la prueba de presión aprobada" sí lo es.
2. **Un paso, una acción, un resultado observable.** Cada paso empieza con un verbo y produce algo que se puede revisar.
3. **Cada paso trae su verificación.** Puede ser una prueba, un validador, un conteo, una consulta o una revisión humana. Sin una verificación que se pueda ejecutar, la única señal de que el trabajo terminó es que "parece terminado" (Anthropic, s. f.).
4. **Dependencias explícitas.** Indique qué pasos requieren otros, que son sus precondiciones. Los pasos independientes pueden hacerse en paralelo.
5. **Concreto y autocontenido.** Nombre los archivos, sistemas, interfaces, datos y responsables. La guía de Claude Code recomienda que una especificación de trabajo nombre los archivos e interfaces involucrados, declare lo que queda fuera del alcance y termine con una verificación de extremo a extremo (Anthropic, s. f.).
6. **Fuera de alcance declarado.** Lo que no se declara fuera del alcance, el agente puede considerarlo dentro.
7. **Granularidad adecuada.** Ni tan general que no oriente, ni tan detallado que repita lo que el agente puede inferir. Si la lista de pasos ya no se revisa de un vistazo, agrúpela en fases con subtareas (descomposición jerárquica).
8. **Aprobación humana antes de lo irreversible.** Borrar, enviar, publicar, pagar o modificar datos en producción requiere un paso de aprobación explícito.
9. **Replanificar de forma explícita.** Cuando un paso falla, se registra la falla y se ajusta el plan. Si cambian el alcance o los riesgos, el plan se vuelve a aprobar.
10. **Una casilla marcada no es una prueba.** El agente puede marcar un paso que no cumplió. La verificación debe ser externa al agente que ejecuta: una prueba, un validador o una revisión independiente. Es el mismo principio del marco LLM-Modulo (Kambhampati et ál., 2024).

### J.6 Lista de chequeo para revisar un plan.md

Se usa antes de aprobar un plan, en el laboratorio 2C y en la evaluación del plan.md del proyecto integrador.

- [ ] El objetivo se puede comprobar con una verificación concreta.
- [ ] El contexto nombra las fuentes, sistemas y datos involucrados, y declara los supuestos.
- [ ] Hay una sección explícita de lo que queda fuera del alcance.
- [ ] Las restricciones no negociables están escritas.
- [ ] Cada paso tiene una acción, un resultado esperado y una verificación.
- [ ] Las dependencias entre pasos son explícitas.
- [ ] Los pasos irreversibles o costosos piden aprobación humana.
- [ ] Los criterios de aceptación incluyen una verificación de extremo a extremo.
- [ ] Los riesgos principales tienen una señal de alerta y una respuesta.
- [ ] El registro de avance está al día y cada replanificación dice qué cambió y por qué.

### J.7 Errores frecuentes

| Error | Consecuencia | Corrección |
|---|---|---|
| Objetivo vago | El agente resuelve otro problema | Objetivo con criterios de aceptación |
| Pasos sin verificación | Los errores aparecen al final, cuando corregirlos cuesta más | Una verificación por paso |
| Sin "fuera de alcance" | Cambios que nadie pidió | Sección de alcance con exclusiones |
| Plan que no se actualiza | El plan deja de describir lo que ocurre y pierde su valor como memoria | Registro de avance actualizado después de cada paso |
| Plan excesivamente detallado | Se vuelve rígido, costoso de mantener y consume contexto | Fases y pasos de nivel adecuado |
| Empezar a actuar mientras se planifica | Se resuelve el problema equivocado | Explorar, planificar, aprobar y solo después ejecutar |
| Aprobar sin leer | La revisión humana deja de ser una validación | Revisión con la lista de chequeo de J.6 |

### J.8 Ejemplo

plan.md de la orden de MantenIA de la sesión 2 (la misma que el bloque 1 resuelve en PDDL), después de una replanificación. Cumple los diez puntos de la lista de chequeo de J.6.

```markdown
# Plan: restablecer la bomba 3 (OT-512)

## Objetivo
Bomba 3 en servicio hoy antes de las ~~14:00~~ 16:00 (plazo aprobado a las
10:40), con el sello cambiado y la prueba de presión aprobada.

## Contexto
- OT-512 (sistema de mantenimiento): fuga en el sello de la bomba 3,
  Planta Norte. Sello SM-40 en la bodega (1 unidad).
- Ana está certificada para la bomba 3; Luis no.
- Supuesto: la línea 2 opera sin la bomba 3.

## Alcance
- Incluye: cambio del sello, prueba y arranque.
- Fuera de alcance: el motor, la línea 2 y las compras.

## Restricciones
- Bloqueo y etiquetado obligatorio; solo personal certificado.

## Pasos
- [x] 1. Retirar el sello SM-40 de la bodega
        → sello en mano · Verif.: salida en inventario
- [x] 2. Bloquear y etiquetar la bomba 3
        → sin energía · Verif.: candado de Ana puesto
- [x] 3. Cambiar el sello (requiere 1 y 2)
        → sello nuevo · Verif.: lista del fabricante
- [ ] 3b. Traer un sello SM-40 de la Planta Sur (nuevo)
        → sello en mano · Verif.: remisión de la Planta Sur
- [ ] 3c. Repetir el cambio de sello (requiere 3b; nuevo)
        → sello nuevo · Verif.: lista del fabricante
- [ ] 4. Prueba de presión (requiere 3c; el primer intento falló)
        → sin fuga · Verif.: 30 min a presión nominal
- [ ] 5. APROBACIÓN: el supervisor autoriza arrancar (requiere 4)
        → autorización · Verif.: firma en la OT-512
- [ ] 6. Retirar el bloqueo y arrancar (requiere 5)
        → en servicio · Verif.: caudal nominal

## Criterios de aceptación
- En servicio antes del plazo, sin fuga tras 30 min y con la OT-512
  cerrada en el sistema de mantenimiento.

## Riesgos y aprobaciones
| Riesgo | Señal | Respuesta |
|---|---|---|
| Sello defectuoso | Fuga en la prueba | Pedir un sello a la Planta Sur |
| Ana no disponible | Aviso de ausencia | Escalar al jefe; no reasignar a Luis |

## Registro de avance
- 09:10 · Paso 1 cumplido (salida en inventario).
- 09:45 · Paso 2 cumplido (candado de Ana puesto).
- 10:20 · Paso 3 cumplido (lista del fabricante).
- 10:30 · Paso 4 falló: fuga; el sello vino defectuoso.
- 10:35 · Replanificación: pasos 3b y 3c; el plazo pasa a las 16:00.
- 10:40 · El supervisor aprueba el nuevo plazo.
```

### J.9 Uso en el curso

- **Sesión 2 (U2):** se presenta en el bloque 3 y se practica en el laboratorio 2C. La plantilla con la lista de chequeo está en los materiales de la sesión.
- **Proyecto integrador:** el plan.md del proyecto se inicia en el cierre de la sesión 2 y su primera versión se entrega al inicio de la semana 2. Desde entonces se actualiza en el laboratorio de proyecto de cada sesión y hace de bitácora. Se revisa con la lista de chequeo de J.6 en la primera versión y en el avance.
- **Hackatón:** cada equipo empieza el reto 1 con un plan.md breve (Anexo C).
- **Agentes de IA (aplicado):** retoma el patrón para construir agentes que generan y ejecutan sus propios planes (Anexo F).

### Fuentes de esta guía

- Anthropic (2025, 29 de septiembre). *Effective context engineering for AI agents*. https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Anthropic (s. f.). *Best practices for Claude Code*. Documentación de Claude Code, consultada el 21 de octubre de 2026. https://code.claude.com/docs/en/best-practices
- Ji, Y. (2025, 18 de julio). *Context Engineering for AI Agents: Lessons from Building Manus*. https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus
- Kambhampati, S. et ál. (2024). *Position: LLMs Can't Plan, But Can Help Planning in LLM-Modulo Frameworks*. ICML 2024. https://proceedings.mlr.press/v235/kambhampati24a.html
- Ghallab, M., Nau, D., Traverso, P. (2025). *Acting, Planning, and Learning*. Cambridge University Press (monitoreo y refinamiento de planes durante la ejecución).
- Anthropic (s. f.). *Choose a permission mode: plan mode*. Documentación de Claude Code. https://code.claude.com/docs/en/permission-modes
- Smith, J. (2025, 7 de octubre). *Introducing Plan Mode*. Cursor. https://cursor.com/blog/plan-mode
- Kiro (s. f.). *Specs*. Documentación. https://kiro.dev/docs/specs/
- GitHub (2025). *Spec Kit* (licencia MIT). https://github.com/github/spec-kit
- Friel, A. (2025, 7 de octubre). *Using PLANS.md for multi-hour problem solving*. OpenAI Cookbook. https://developers.openai.com/cookbook/articles/codex_exec_plans
