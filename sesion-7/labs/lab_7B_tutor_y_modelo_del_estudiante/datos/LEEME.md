# Los técnicos del contrapunto

`tecnicos_contrapunto.csv` tiene 10 técnicos **simulados**. No son personas reales.

- **El curso:** la inducción de los técnicos nuevos de MantenIA, una empresa ficticia.
- **La habilidad:** la alineación de una bomba, con dominio inicial 0.10, aprendizaje 0.12, adivinanza 0.15 y descuido 0.10.
- **Cómo se simularon:** con el mismo modelo de la sección 4 del notebook y la semilla 2026. Cada técnico hizo 8 ejercicios.

| Columna | Qué es |
| :--- | :--- |
| `tecnico` | Un código, de T01 a T10 |
| `habilidad` | Alineación de una bomba |
| `respuestas` | Las 8 respuestas, en orden: ✓ si acertó, ✗ si falló |
| `domina_al_terminar` | El estado oculto: si domina la habilidad al terminar. El notebook lo usa solo para evaluar, y el LLM nunca lo ve |

Hay tres pares de técnicos con las mismas respuestas: T01 y T03, T02 y T05, y T08 y T09. Así puedes ver si el LLM les da el mismo dominio estimado.
