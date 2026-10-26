# Sesión 3 · Trabajo independiente

**Sistemas Inteligentes · Especialización en Inteligencia Artificial · UNAL Manizales**
Unidad 3: Razonamiento Automático: Solvers, Restricciones y Razonamiento en LLMs

| Trabajo | Charla | Tipo | Tiempo estimado | Entrega |
|---|---|---|---|---|
| TI-1 · Su problema de asignación como modelo de restricciones | Inicial · Dos formas de razonar | Ejercicio individual | 65 min | Inicio de la semana 3 |
| TI-2 · Ponga a prueba una política de su organización | Intermedia · Verificar con lógica | Ejercicio individual | 70 min | Inicio de la semana 3 |
| Paso del proyecto integrador | De cierre · Cuándo confiar en cada uno | En equipo | 60 min | Inicio de la semana 3 |
| **Total** | | | **3 h 15 min** | |

**Sobre el tiempo.** Cada sesión del bloque presencial genera unas 12 horas de trabajo independiente (Anexo A del programa). Estos dos trabajos y el paso del proyecto ocupan 3 h 15 min. El resto se dedica a terminar los laboratorios 3A y 3B y a la lectura de la sesión 4.

**Ninguno pide programar.** Se hacen con un LLM, papel o una hoja de cálculo, y con los notebooks de los laboratorios cambiando datos en sus celdas de configuración.

**Formato de entrega.** Un archivo PDF por trabajo, por el canal del curso. Los dos trabajos son individuales; el paso del proyecto es del equipo. Puede usar asistentes de IA generativa como herramienta de consulta, declarando cómo los usó; en los dos trabajos el LLM es parte del ejercicio.

**Datos confidenciales.** No escriba en un LLM información confidencial de su organización (nombres de clientes, cifras, datos personales). Anonimice o cambie los datos antes.

---

## TI-1 · Su problema de asignación como modelo de restricciones

**Charla inicial · 65 minutos**

**Propósito.** Practicar la descripción de un problema como modelo de restricciones, la misma que se le da a un asistente de IA en el Laboratorio 3A, y la verificación de una solución propuesta por un LLM.

**Instrucciones**

1. Elija un problema de asignación de su organización: turnos de personal, horarios de salas o reuniones, personas a proyectos, vehículos a rutas. Que sea pequeño: de 3 a 6 personas o recursos, y de 3 a 7 periodos o tareas.
2. Descríbalo en una tabla con las cuatro partes de un modelo, como el de los turnos de MantenIA en la charla inicial:
   - **Variables:** la pregunta que hay que responder para cada combinación (por ejemplo, «¿la persona P trabaja el turno T?»).
   - **Dominios:** las respuestas posibles.
   - **De 3 a 5 restricciones duras:** reglas que no se negocian. Al menos una debe venir de una norma o política real de su organización; señálela.
   - **De 2 a 3 restricciones blandas,** cada una con un peso, y el **objetivo**.
3. Pídale a un LLM una solución con cadena de pensamiento. Por ejemplo:

   > Resuelve este problema de asignación. Variables: [pegue]. Restricciones que se deben cumplir siempre: [pegue]. Preferencias con su peso: [pegue]. Objetivo: [pegue]. Razona paso a paso y entrega al final la asignación como una tabla.

4. **Verifique la solución a mano**, regla por regla, en una tabla con estas columnas: restricción, ¿se cumple? (sí o no, y dónde falla). Calcule la penalización de las restricciones blandas.
5. Pida la solución dos veces más, en conversaciones nuevas, y compare las tres: ¿coinciden?, ¿alguna cumple todas las reglas duras? Es la idea de la autoconsistencia, hecha a mano.
6. **Opcional, para comprobar con un solver sin programar:**
   - Use vibe coding, como en el Laboratorio 3A: pídale a un asistente de IA un programa que resuelva su problema con un solver y que imprima si se cumple cada regla. Compare su salida con su verificación a mano.
   - O use el complemento Solver de una hoja de cálculo con variables binarias (ver «Apoyo»).
7. Responda en media página:
   - ¿Qué reglas violó el LLM, si violó alguna?
   - ¿Qué cree que pasaría con 30 personas y un mes completo?
   - Para este problema en su organización, ¿usaría un solver, un LLM o los dos? Justifique con la guía de decisión de la charla de cierre.

**Entregable.** PDF de 1 a 2 páginas con el modelo (tabla), la instrucción, las tres respuestas del LLM, la tabla de verificación y la reflexión.

**Criterios de evaluación**

| Criterio | Peso |
|---|---|
| Modelo bien formado: variables, dominios, restricciones duras y blandas bien distinguidas, objetivo | 40 % |
| Verificación correcta y completa de las tres soluciones | 40 % |
| Reflexión con los conceptos de la sesión: garantía, autoconsistencia, crecimiento combinatorio | 20 % |

**Apoyo**
- Google OR-Tools, [«Optimización de restricciones»](https://developers.google.com/optimization/cp?hl=es-419) y [«Programación de empleados»](https://developers.google.com/optimization/scheduling/employee_scheduling?hl=es-419). Explican qué es un modelo de restricciones con un ejemplo de turnos de enfermería. La versión en español está traducida automáticamente; el original en inglés está [aquí](https://developers.google.com/optimization/cp). La descripción del problema se entiende sin leer el código.
- Poole, D. y Mackworth, A. (2023). [*Artificial Intelligence: Foundations of Computational Agents*, 3.ª ed., sección 4.1, «Variables and Constraints»](https://artint.info/3e/html/ArtInt3e.Ch4.S1.html). Texto abierto, en inglés.
- Para el paso opcional con una hoja de cálculo:
  - Microsoft, [«Uso de Solver para programar el personal»](https://support.microsoft.com/es-es/office/using-solver-to-schedule-your-workforce-7ae8dd69-7582-4f41-83f1-ea3543398b46), un ejemplo de turnos en español. El Solver de Excel es un complemento gratuito, pero solo funciona en la versión de escritorio, no en Excel para la web.
  - Alternativa libre: [Solver de LibreOffice Calc](https://help.libreoffice.org/latest/es/text/scalc/01/solver.html), en español.

---

## TI-2 · Ponga a prueba una política de su organización

**Charla intermedia · 70 minutos**

**Propósito.** Practicar la verificación formal de un conjunto de reglas y comparar lo que encuentra un LLM con lo que encuentra un solver lógico, como en el Laboratorio 3B.

**Instrucciones**

1. Elija una política real de su organización que use montos, plazos o roles: aprobación de compras o gastos, descuentos, vacaciones, viáticos, horas extra. Anonimícela.
2. Escríbala como **5 a 8 reglas «si… entonces…»**, como la política de compras de MantenIA en la charla intermedia. Conserve las palabras del texto original sobre los bordes: «menos de», «hasta», «más de».
3. Pídale a un LLM que la revise. Por ejemplo:

   > Revisa estas reglas: [pegue]. ¿Hay algún caso en que dos reglas se contradicen? ¿Hay casos que ninguna regla cubre? Para cada problema que encuentres, da un caso concreto, con valores, que lo muestre.

   Registre sus hallazgos.
4. Cargue las mismas reglas en la tabla de configuración del notebook del Laboratorio 3B y ejecute las verificaciones con Z3. Registre sus respuestas y contraejemplos.
5. Compare en una tabla con estas columnas: problema, ¿lo encontró el LLM?, ¿lo encontró Z3?, contraejemplo. **Verifique a mano** cada contraejemplo contra las reglas.
6. Corrija la política y vuelva a verificar, hasta que Z3 responda `unsat` a las preguntas de contradicción y de laguna.
7. Responda en media página:
   - ¿El LLM encontró algo que Z3 no encontró, o al revés?
   - ¿El LLM señaló problemas que no existían?
   - Si tuviera que presentar el resultado a la gerencia, ¿qué explicación usaría, la del LLM o el contraejemplo de Z3? ¿Por qué?

**Entregable.** PDF de 1 a 2 páginas con las reglas originales y las corregidas, los hallazgos del LLM, los contraejemplos de Z3, la tabla comparativa y la reflexión.

**Criterios de evaluación**

| Criterio | Peso |
|---|---|
| Reglas bien escritas y fieles al texto de la política | 30 % |
| Comparación correcta, con los contraejemplos verificados a mano | 40 % |
| Reflexión con los conceptos de la sesión: contraejemplo, `unsat` como prueba, fidelidad de las explicaciones | 30 % |

**Para leer con criterio.** Si Z3 responde `unsat`, la garantía es sobre las reglas que usted escribió. Si al pasar el texto a reglas cambió un «menos de» por un «hasta», Z3 verificó otra política.

**Apoyo**
- Amazon Web Services, [«¿Qué es el razonamiento automatizado?»](https://aws.amazon.com/es/what-is/automated-reasoning/). Introducción en español, sin código.
- Cook, B. (2021). [«A gentle introduction to automated reasoning»](https://www.amazon.science/blog/a-gentle-introduction-to-automated-reasoning). Amazon Science, en inglés. Escrito para profesionales que no conocen el área.
- Sobre la fidelidad de las explicaciones de un LLM:
  - En español: Torrijos, C. (2025). [«Pensar en voz alta: prompts para simular con IA el razonamiento humano»](https://datos.gob.es/es/blog/pensar-en-voz-alta-prompts-para-simular-con-ia-el-razonamiento-humano). datos.gob.es.
  - En inglés: Anthropic (2025). [«Reasoning models don't always say what they think»](https://www.anthropic.com/research/reasoning-models-dont-say-think).

---

## Paso del proyecto integrador

**Charla de cierre · en equipo · 60 minutos**

**Propósito.** Llevar la Unidad 3 al caso del proyecto: qué debe garantizarse, cómo se verifica y qué se puede delegar a un LLM.

**Instrucciones**

1. Agregue al plan.md del proyecto un paso para identificar las **restricciones duras y blandas** del caso. Confírmelas con quien conoce el proceso en la organización.
2. Agregue un paso para decidir **cómo se verifica cada regla**: con un solver, con un validador o con una revisión humana. Hágalo en una tabla regla-verificador.
3. Agregue un paso para elegir **qué razonamiento se delega a un LLM** y quién lo verifica. Use la guía de decisión de la charla de cierre y justifique la elección.
4. Cada paso nuevo lleva su resultado y su verificación, como pide la plantilla.
5. Revise el plan.md completo con la lista de chequeo (J.6) que está al final de `plantilla_plan.md` (en la carpeta de la sesión 2).

**Entregable.** El plan.md actualizado, con la lista de chequeo marcada y la tabla regla-verificador.

**Criterios de evaluación**

| Criterio | Peso |
|---|---|
| Restricciones del caso bien identificadas y separadas en duras y blandas | 35 % |
| Tabla regla-verificador coherente con la guía de decisión | 35 % |
| plan.md que cumple la lista de chequeo | 30 % |

---

## Lectura obligatoria para la sesión 4

Radford, A., Kim, J. W., Hallacy, C. et al. (2021). *Learning Transferable Visual Models From Natural Language Supervision*. ICML 2021, PMLR 139, 8748–8763. <https://proceedings.mlr.press/v139/radford21a.html>

Se asignan la introducción, el enfoque y la discusión de limitaciones.
