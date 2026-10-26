# Laboratorio 3A · Vibe coding: la logística de una empresa de aseo

**Sistemas Inteligentes · Sesión 3 · 60 minutos en clase y hasta 30 en casa, en parejas**

En este laboratorio no se escribe código a mano. Ustedes describen un problema a un asistente de IA, el asistente escribe un programa que lo resuelve con un solver, y ustedes comprueban si el programa hace lo que pidieron. Eso es el *vibe coding*: «usar inteligencia artificial, guiada con lenguaje natural, para escribir código» (Collins, palabra del año 2025; el término es de Andrej Karpathy, 2025). Pero olvidar el código no es olvidar verificar: la responsabilidad de que el programa cumpla las reglas sigue siendo de ustedes.

**El asistente.** Sirve el que ya tienen: Claude, con la extensión Claude Code en VS Code o en [claude.ai](https://claude.ai); o Gemini, con la extensión Antigravity en VS Code o en [gemini.google.com](https://gemini.google.com). En VS Code, abran la carpeta del curso para que el programa use el entorno `.venv`. En el navegador, el asistente les da el programa y ustedes lo ejecutan en VS Code.

Aseo Bruma y todos sus datos son ficticios. **No pegue en un asistente datos reales de su organización.**

**Tiempos sugeridos:** 20 minutos para leer el problema y escribir la descripción del modelo; 25 para obtener la primera solución y comprobarla; 15 para los escenarios. La tabla de hallazgos y el PDF se terminan en casa.

## 1. El problema

Aseo Bruma es una pequeña empresa de aseo. Cada tarde, la coordinadora arma a mano la programación del día siguiente: quién atiende cada servicio y a qué hora. Este es el miércoles.

**Personal.** Cada persona parte de su zona al inicio de su jornada y debe terminar su último servicio a más tardar al fin de su jornada.

| Persona | Zona de partida | Inicio de jornada | Fin de jornada | Habilidades |
|---|---|---|---|---|
| Carmen | Norte | 07:00 | 15:00 | alturas, químicos |
| Wilson | Centro | 08:00 | 17:00 | maquinaria, químicos |
| Yuliana | Oriente | 07:00 | 13:00 | (ninguna especial) |
| Andrés | Sur | 09:00 | 17:00 | alturas, maquinaria |

**Servicios.** La ventana dice entre qué horas puede *empezar* cada servicio.

| Servicio | Cliente | Zona | Puede empezar entre | Duración | Habilidad que exige |
|---|---|---|---|---|---|
| S1 | Clínica Los Alpes | Norte | 07:00 y 09:00 | 120 min | químicos |
| S2 | Oficinas Torre Centro | Centro | 08:00 y 11:00 | 150 min | alturas |
| S3 | Colegio San Rafael | Sur | 12:00 y 14:30 | 120 min | maquinaria |
| S4 | Apartamento Pérez | Norte | 09:00 y 12:00 | 90 min | — |
| S5 | Restaurante El Fogón | Centro | 14:00 y 15:30 | 90 min | químicos |
| S6 | Bodega Logística Sur | Sur | 07:00 y 10:00 | 180 min | maquinaria |
| S7 | Consultorio Dental Sonrisa | Oriente | 10:00 y 13:00 | 60 min | químicos |
| S8 | Casa Gómez | Oriente | 08:00 y 11:00 | 120 min | — |
| S9 | Local comercial La Avenida | Centro | 11:00 y 14:00 | 60 min | — |
| S10 | Edificio Mirador | Oriente | 13:00 y 15:00 | 120 min | alturas |

**Tiempos de viaje entre zonas, en minutos.** Dentro de una misma zona el viaje es de 10 minutos, también desde la zona de partida hasta un primer servicio en esa zona.

| | Norte | Centro | Sur | Oriente |
|---|---|---|---|---|
| **Norte** | 10 | 20 | 35 | 25 |
| **Centro** | 20 | 10 | 20 | 20 |
| **Sur** | 35 | 20 | 10 | 30 |
| **Oriente** | 25 | 20 | 30 | 10 |

**Reglas que siempre se cumplen**
- R1. Cada servicio lo atiende exactamente una persona.
- R2. Cada servicio empieza dentro de su ventana. Si la persona llega antes, espera.
- R3. Quien atiende un servicio tiene la habilidad que el servicio exige.
- R4. Una persona no hace dos servicios a la vez. Parte de su zona al inicio de su jornada, y antes de cada servicio necesita el tiempo de viaje desde donde estaba.
- R5. Cada persona termina su último servicio a más tardar al fin de su jornada; terminar justo a esa hora está permitido. El regreso a su zona no cuenta.

**Preferencias, en puntos de penalización**
- P1. Viajar poco: 1 punto por cada minuto de viaje, desde la zona de partida hasta el primer servicio y entre servicios. El regreso a casa no cuenta.
- P2. El Apartamento Pérez pide que lo atienda Yuliana: 60 puntos si lo atiende otra persona, también si Yuliana no trabaja ese día.
- P3. Carga pareja entre las personas de jornada completa (Carmen, Wilson y Andrés), sin contar a quien falte ese día: 1 punto por cada minuto de diferencia entre la que más minutos de servicio tiene y la que menos. Los minutos de servicio son la suma de las duraciones, sin los viajes; quien no tenga servicios cuenta con 0.

**Objetivo:** cumplir todas las reglas con el menor total de puntos.

**Escenarios, para después de la primera solución.** Cada escenario parte del día base: no se acumulan. Los puntos solo se comparan dentro de un mismo escenario.
- E1. A última hora llama la Notaría Segunda (zona Centro): un servicio de 60 minutos que puede empezar entre las 15:00 y las 16:00, sin habilidad especial.
- E2. Yuliana avisa que no puede trabajar el miércoles.
- E3. En lugar de Yuliana, la que no puede trabajar es Carmen.

## 2. El prompt

Copie el bloque en su asistente. Antes, complete la «Descripción del modelo» con sus palabras: es el corazón del laboratorio. Use la anatomía de un modelo de restricciones: qué se decide (variables), qué reglas se cumplen siempre, qué preferencias hay y con qué peso, y qué se busca (objetivo). Explique las reglas y preferencias de la sección 1 como a un programador, sin omitir ningún dato.

```text
Actúa como programador. Escribe un programa en Python que resuelva el problema
de programación de servicios de una empresa de aseo que describo abajo.

DATOS: [pegue aquí la sección 1 desde «Personal» hasta antes de «Reglas»:
las tres tablas con las frases que las acompañan; y los escenarios E1, E2 y E3]

DESCRIPCIÓN DEL MODELO (complete con sus palabras):
- Lo que hay que decidir: ...
- Reglas que siempre se cumplen: ...
- Preferencias, con sus puntos: ...
- Objetivo: ...

REQUISITOS:
1. Usa el solver CP-SAT de OR-Tools (paquete ortools). Si no está instalado,
   dime el comando exacto para instalarlo en mi entorno de Python.
2. Antes de escribir el código, lista en español las reglas y preferencias que
   vas a programar, una por línea, para que yo las compare con las mías.
3. Imprime la programación de cada persona en orden: servicio, cliente, zona,
   hora de inicio y hora de fin.
4. Imprime los puntos de cada preferencia y el total, y si la solución es
   óptima (la mejor posible) o solo factible (cumple las reglas).
5. Al final, revisa la solución regla por regla, con código separado del
   modelo, e imprime si cada regla se cumple.
6. Si no hay solución, dilo claramente. Nunca inventes una.
7. Agrega un caso pequeño, de 2 personas y 3 servicios, cuya solución yo pueda
   revisar a mano, y una forma sencilla de correr los escenarios E1, E2 y E3.
8. Explícame en español qué archivos lee y escribe el programa y cómo
   ejecutarlo.
```

Si el programa falla, péguele al asistente el mensaje de error completo.

## 3. Antes de confiar en el programa

Un programa que corre no es un programa correcto. Hagan estas cuatro comprobaciones:

- **Compare las reglas.** Ponga la lista del requisito 2 al lado de las reglas y preferencias de la sección 1. ¿Falta alguna? ¿Cambió un «a más tardar» por un «antes de», o una ventana de inicio por una de fin?
- **Revise a mano** que el caso pequeño del requisito 7 cumpla las reglas, y el recorrido completo de Wilson en el día base, con la tabla de viajes en la mano. El solver puede elegir cualquier hora válida, no necesariamente la más temprana: eso no es un error.
- **Lea con desconfianza las explicaciones del asistente.** Compare cada afirmación con las salidas: ¿la preferencia que dice que cambió de verdad cambió? La revisión del requisito 5 la escribió la misma IA que escribió el modelo: si entendió mal una regla, puede revisarla con el mismo error.
- **Corra los tres escenarios** y pregúntese si cada resultado tiene sentido para la coordinadora de Aseo Bruma. «No hay solución» puede ser la respuesta correcta: si un escenario no la tiene, expliquen qué reglas lo impiden.

Si encuentran un error, corrijan la descripción del modelo o pídanle al asistente que lo arregle, y vuelvan a comprobar. Lo que no alcancen en clase lo terminan en casa.

## 4. Qué se entrega

Al inicio de la semana 3, junto con los trabajos independientes, un PDF por pareja con:
- el prompt que usaron, con su descripción del modelo;
- el programa que escribió el asistente y lo que imprimió en su última corrida: el caso pequeño, el día base y los tres escenarios;
- una tabla corta: qué omitió, cambió o inventó el asistente, y cómo lo detectaron;
- para el escenario sin solución, si lo hay, qué cambio le propondrían a la coordinadora, comprobado con el programa;
- la declaración de uso de asistentes de IA: qué asistente y qué modelo usaron, y cuántas veces le pidieron correcciones, al código o a sus explicaciones.

**Referencias:** Karpathy, A. (2025, 2 de febrero), [publicación en X](https://x.com/karpathy/status/1886192184808149383) ([copia en Wayback Machine](https://web.archive.org/web/20251005055913/https://twitter.com/karpathy/status/1886192184808149383)). Collins (2025, 6 de noviembre), [Collins' Word of the Year 2025: AI meets authenticity as society shifts](https://blog.collinsdictionary.com/language-lovers/collins-word-of-the-year-2025-ai-meets-authenticity-as-society-shifts/). [Documentación de CP-SAT](https://developers.google.com/optimization/cp/cp_solver), Google OR-Tools.
