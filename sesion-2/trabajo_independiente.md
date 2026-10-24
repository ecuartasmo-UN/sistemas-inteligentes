# Sesión 2 · Trabajo independiente

**Sistemas Inteligentes · Especialización en Inteligencia Artificial · UNAL Manizales**
Unidad 2: Planificación Automática en IA

| Trabajo | Bloque | Tipo | Tiempo estimado | Entrega |
|---|---|---|---|---|
| TI-1 · Su proceso como problema de planificación | 1 · Planificación automática clásica | Ejercicio | 70 min | Inicio de la semana 2 |
| TI-2 · Ponga a prueba a un LLM como planificador | 2 · LLMs y planificación | Ejercicio | 65 min | Inicio de la semana 2 |
| TI-3 · El plan.md de una tarea real de su trabajo | 3 · Planes explícitos en agentes (plan.md) | Ejercicio | 75 min | Inicio de la semana 2 |
| **Total** | | | **3 h 30 min** | |

**Sobre el tiempo.** Cada sesión del bloque presencial genera unas 12 horas de trabajo independiente (Anexo A del programa). Estos tres trabajos ocupan 3 h 30 min. El resto se dedica a terminar los laboratorios 2A, 2B y 2C, a la primera versión del plan.md del proyecto integrador y a la lectura de la sesión 3.

**Los tres trabajos están encadenados.** El problema que formalice en el TI-1 es el que pondrá a prueba con un LLM en el TI-2. Conviene hacerlos en ese orden.

**Formato de entrega.** Un archivo PDF por trabajo, por el canal del curso. Los trabajos son individuales. Puede usar asistentes de IA generativa como herramienta de consulta, declarando cómo los usó; en el TI-2 y el TI-3 el LLM es parte del ejercicio.

**Datos confidenciales.** No escriba en un LLM información confidencial de su organización (nombres de clientes, cifras, datos personales). Anonimice o cambie los datos antes.

---

## TI-1 · Su proceso como problema de planificación

**Bloque 1 · 70 minutos**

**Propósito.** Practicar la formalización de un problema de planificación: estados descritos con hechos, acciones con precondiciones y efectos, y un plan que se pueda verificar paso a paso.

**Instrucciones**

1. Elija un proceso de su organización con reglas claras y varios pasos. Por ejemplo: aprobar una compra, despachar un pedido, incorporar a un empleado nuevo o cerrar un mes contable.
2. Identifique los objetos (personas, documentos, equipos, lugares) y escriba entre 5 y 8 **hechos** que describan el estado inicial, en la forma `(predicado objeto …)`. Por ejemplo: `(solicitud-recibida s1)`.
3. Escriba la **meta** como uno o dos hechos que deben ser ciertos al final.
4. Defina entre 3 y 4 **acciones**. Para cada una, indique sus parámetros, sus precondiciones, los hechos que agrega y los hechos que elimina. Puede hacerlo en una tabla o en PDDL, siguiendo el ejemplo de MantenIA del Bloque 1.
5. Al menos una precondición debe representar una **regla de negocio** real: una aprobación, un requisito legal, una certificación o un límite de presupuesto. Señálela.
6. **Trace a mano un plan** de 4 a 6 pasos. Para cada paso, muestre qué precondiciones se cumplen y cómo cambia el estado (qué hechos se agregan y cuáles se eliminan), hasta llegar a la meta.

**Opcional, para quien quiera comprobarlo con un planificador real** (no requiere cuenta ni instalación):
1. Abra el editor en línea [editor.planning.domains](https://editor.planning.domains/) y espere unos segundos a que aparezca el botón **Solver** en la barra.
2. Pegue su dominio en la pestaña inicial; con **File → New**, abra otra pestaña y pegue su problema.
3. Pulse **Solver**, elija el planificador **LAMA-first** y pulse **Plan**. El plan aparece en una pestaña nueva. Compárelo con el suyo.

Use nombres sin tildes ni ñ (`tecnico`, no `técnico`): con ellos el planificador falla sin mostrar error. Si algo no funciona, pruebe el planificador **BFWS-FF**, que sí muestra los errores de sintaxis. No escriba datos sensibles: el editor envía el PDDL a un servidor externo con fines educativos.

**Entregable.** PDF de 1 a 2 páginas con los objetos, el estado inicial, la meta, las acciones (tabla o PDDL), la regla de negocio señalada y la traza del plan.

**Criterios de evaluación**

| Criterio | Peso |
|---|---|
| Acciones bien formadas: precondiciones y efectos completos y coherentes | 40 % |
| Traza correcta: cada paso cumple sus precondiciones y el estado cambia como dicen los efectos | 40 % |
| Regla de negocio bien modelada como precondición | 20 % |

**Apoyo**
- El dominio y el problema de MantenIA del Bloque 1 están en la carpeta `ejemplo_pddl/` de la sesión: úselos como modelo.
- Helmert, M. [*An Introduction to PDDL*](https://gki.informatik.uni-freiburg.de/teaching/ws0809/aip/pddl-folien.pdf) (Universidad de Freiburg): 15 diapositivas que explican cada acción primero en palabras (descripción, precondición, efecto) y luego en PDDL. En inglés.
- Referencia de la sintaxis en [planning.wiki](https://planning.wiki/ref/pddl/domain) (dominio) y [aquí](https://planning.wiki/ref/pddl/problem) (problema). Sus ejemplos son para leer, no para ejecutar.
- En español, para los conceptos (no enseña la sintaxis de PDDL): Garrido, A. (2018). [*Planificación en Inteligencia Artificial*](https://riunet.upv.es/handle/10251/101003). Video, Universitat Politècnica de València.
- Russell y Norvig (2021), *Artificial Intelligence: A Modern Approach* (4.ª ed.), capítulo 11, «Automated Planning».

---

## TI-2 · Ponga a prueba a un LLM como planificador

**Bloque 2 · 65 minutos**

**Propósito.** Comprobar por cuenta propia lo que discutimos en el club de lectura y en el Bloque 2: si un LLM produce planes válidos, y qué pasa cuando cambian los nombres pero no la estructura del problema.

**Instrucciones**

1. Tome el problema de su TI-1 (acciones, estado inicial y meta).
2. Pídale a un LLM un plan con una instrucción como esta:

   > Actúa como planificador. Estas son las acciones disponibles, con sus precondiciones y efectos: [pegue sus acciones]. Estado inicial: [pegue los hechos]. Meta: [pegue la meta]. Devuelve un plan como una lista numerada de acciones con sus parámetros. Cada acción solo se puede aplicar si se cumplen todas sus precondiciones.

3. **Verifique el plan a mano**, paso a paso, en una tabla con estas columnas: paso, acción, ¿se cumplen todas las precondiciones? (sí/no y cuál falla), hechos que cambian. Indique si el plan alcanza la meta.
4. **Ofusque los nombres**, como en *Mystery Blocksworld*: reemplace cada nombre de acción, predicado y objeto por una palabra sin sentido (por ejemplo, `aprobar` → `zelfar`, `solicitud` → `brumo`). La estructura del problema queda idéntica. Pida otra vez el plan y verifíquelo igual.
5. **Opcional:** si escribió su problema en PDDL en el TI-1, valide los planes del LLM con VAL desde el editor en línea. Pegue el plan en una pestaña nueva (una acción por línea, entre paréntesis), pulse **Solver**, elija **VAL** y luego la pestaña del plan. Lea el texto del resultado: «plan valid» o «plan failed» con la precondición que falla. La pestaña se titula «Found Plan» aunque el plan sea inválido.
6. Responda en media página:
   - ¿En cuál de las dos versiones fue mejor el LLM? ¿Qué tipo de errores cometió: precondiciones incumplidas, pasos faltantes, acciones inventadas, meta no alcanzada?
   - Si tuviera que usar ese LLM en su organización, ¿qué verificador pondría a su lado, al estilo LLM-Modulo?

**Entregable.** PDF de 1 a 2 páginas con las dos instrucciones, los dos planes del LLM, las dos tablas de verificación y la reflexión.

**Criterios de evaluación**

| Criterio | Peso |
|---|---|
| Verificación correcta y completa de ambos planes | 50 % |
| Ofuscación bien hecha: la estructura del problema se conserva | 20 % |
| Reflexión con los conceptos de la sesión: verificación externa, LLM-Modulo, críticos | 30 % |

**Para leer con criterio.** Un solo problema no permite generalizar: el resultado depende del LLM, de la instrucción y del problema. Lo valioso del ejercicio es el método de verificación, no la nota que saque el LLM.

**Apoyo.** Los dominios de Blocksworld y de su versión ofuscada (Mystery Blocksworld) que usa PlanBench están en el [repositorio de los autores](https://github.com/karthikv792/LLMs-Planning/tree/main/plan-bench/instances/blocksworld) (licencia MIT): sirven de modelo para su ofuscación.

---

## TI-3 · El plan.md de una tarea real de su trabajo

**Bloque 3 · 75 minutos**

**Propósito.** Practicar la revisión crítica de un plan explícito redactado por un LLM, con la lista de chequeo del Anexo J del programa.

**Instrucciones**

1. Elija una tarea real de su trabajo que tome entre una y dos semanas y toque varias partes: una auditoría, un cierre de mes, una migración de sistema, un evento, el lanzamiento de un producto.
2. Pídale a un LLM que redacte el plan.md de esa tarea con la estructura de `plantilla_plan.md`. Descríbale el contexto, sin datos confidenciales.
3. Revise el plan del LLM con la **lista de chequeo** que está al final de la plantilla. Anote qué puntos no cumple.
4. Corrija el plan hasta que cumpla los diez puntos.
5. Haga una tabla con **al menos 5 cambios**: qué decía el LLM, qué dice ahora y qué punto de la lista de chequeo motivó el cambio.

**Entregable.** PDF con las dos versiones del plan.md (la del LLM y la corregida), la lista de chequeo marcada para cada versión y la tabla de cambios. Extensión libre para los planes; una página para la tabla.

**Criterios de evaluación**

| Criterio | Peso |
|---|---|
| Revisión rigurosa con la lista de chequeo (errores bien identificados) | 40 % |
| Plan corregido: objetivo verificable, pasos con verificación, alcance y aprobaciones | 40 % |
| Tabla de cambios clara y justificada | 20 % |

**Apoyo**
- `plantilla_plan.md`, en la carpeta de la sesión.
- Anexo J del programa: guía para escribir un plan.md correcto.
- Anthropic (s. f.). [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices): secciones «Explore first, then plan, then code» y «Give Claude a way to verify its work». En inglés.

---

## Lectura obligatoria para la sesión 3

Trinh, T. H., Wu, Y., Le, Q. V., He, H. y Luong, T. (2024). *Solving olympiad geometry without human demonstrations*. Nature 625, 476–482. Acceso abierto: <https://www.nature.com/articles/s41586-023-06747-5>
