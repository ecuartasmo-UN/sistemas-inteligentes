# Datos y modelos del Laboratorio 5B: origen y licencia

## `datos/ordenes.csv`: órdenes de trabajo de MantenIA

- **Autoría:** escritas para el curso *Sistemas Inteligentes* (UNAL Manizales) en octubre de 2026. Son **ficticias**: ninguna viene de una organización real, y no contienen datos personales. MantenIA es una empresa ficticia.
- **Contenido:** 258 órdenes en español, con el equipo que debe atenderlas (eléctrico, mecánico, fugas o instrumentación):
  - 200 de entrenamiento, 50 por equipo;
  - 48 de prueba, 12 por equipo, escritas con otras palabras que las de entrenamiento;
  - 10 para poner a prueba las arquitecturas: 8 trampas, con negaciones y palabras engañosas, y 2 órdenes de control, que dicen lo mismo sin trampa.
- **Uso:** material del curso, para el laboratorio y los trabajos independientes.

## `mis_textos/ejemplo.csv`

36 solicitudes internas ficticias de MantenIA, en tres clases (compras, sistemas y talento humano), escritas para el curso como modelo del formato de los textos propios. Misma autoría y uso.

## El transformer: Granite Embedding 107M multilingüe

- **Autoría:** IBM. *Granite embedding models* (2025). <https://arxiv.org/abs/2502.20204>
- **Fuente:** <https://huggingface.co/ibm-granite/granite-embedding-107m-multilingual>, versión `d6cffd338414d6a1c1f5decfad5fec62eebc90d5`. Se descarga del Hugging Face Hub la primera vez que se usa (214 MB); no viene en esta carpeta.
- **Licencia:** Apache-2.0.
- **Uso:** congelado, sin ajustarlo. El vector de cada texto es el del primer token (CLS), normalizado, como indica su ficha.

## Las respuestas grabadas del LLM

`grabaciones/respuestas.json` tiene respuestas reales de Claude Haiku 5.5 (Anthropic), obtenidas por la API el 29 de octubre de 2026 con la instrucción de la sección 7, para las 48 órdenes de prueba y las 10 trampas y controles, en tres corridas.
