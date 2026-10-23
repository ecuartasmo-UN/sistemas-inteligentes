# Instalación del entorno del curso · Sistemas Inteligentes

**Especialización en Inteligencia Artificial · UNAL Manizales · Fase previa (antes de la sesión 1)**

Los laboratorios del curso son notebooks de Jupyter que se trabajan en **VS Code**, en su propio computador. Esta guía instala todo lo necesario en unos 30 a 45 minutos. Al final, un notebook corto comprueba que todo funciona.

Va a instalar:
1. Python 3.13 (sirve también 3.12).
2. VS Code, con las extensiones **Python** y **Jupyter** de Microsoft.
3. Un **entorno virtual del curso** (una carpeta `.venv`) con las librerías de los laboratorios.
4. El acceso a un modelo de lenguaje: una clave de API y, si quiere, un modelo local.

## 1. Python 3.13

**Windows.** Descargue el instalador de Python 3.13 desde [python.org/downloads](https://www.python.org/downloads/). En la primera pantalla marque **Add python.exe to PATH** y luego elija **Install Now**. Para comprobarlo, abra una terminal (PowerShell) y escriba `py -3.13 --version`.

**macOS.** Descargue el instalador de Python 3.13 para macOS desde [python.org/downloads](https://www.python.org/downloads/) y ejecútelo. Para comprobarlo, abra la Terminal y escriba `python3.13 --version`.

**Linux.** Instálelo con el gestor de paquetes de su distribución, si lo ofrece (paquetes `python3.13` y `python3.13-venv`). Si no, use [uv](https://docs.astral.sh/uv/): `uv python install 3.13`.

## 2. VS Code y sus extensiones

1. Instale VS Code desde [code.visualstudio.com](https://code.visualstudio.com/).
2. Ábralo, vaya a la vista de **Extensiones** (Ctrl + Shift + X; en macOS, Cmd + Shift + X) e instale **Python** y **Jupyter**, las dos publicadas por Microsoft.

## 3. La carpeta del curso y su entorno virtual

1. Cree una carpeta para el curso, sin tildes ni espacios en el nombre; por ejemplo, `SistemasInteligentes`.
2. Copie dentro la carpeta `entorno` y, a medida que el docente las entregue, las carpetas de los laboratorios.
3. En VS Code, abra la carpeta del curso con **Archivo › Abrir carpeta**.
4. Abra la paleta de comandos (Ctrl + Shift + P; en macOS, Cmd + Shift + P), escriba **Python: Create Environment** y elíjalo. Luego:
   - elija **Venv**;
   - elija Python 3.13;
   - marque `entorno/requirements.txt` para instalar sus librerías.
5. Espere unos minutos. VS Code crea la carpeta `.venv` e instala las librerías.

Cada laboratorio trae su propio `requirements.txt`. La primera celda de cada notebook instala lo que falte, así que no tiene que hacerlo a mano.

## 4. Acceso a un modelo de lenguaje

**Clave de API.** El docente le indicará cómo obtener la clave del curso. Cree en la carpeta del curso un archivo llamado `.env` (con el punto al inicio) que tenga **una sola línea**, sin espacios, sin comillas y sin un `=` de más:

```
ANTHROPIC_API_KEY=sk-ant-...
```

La clave es personal: no la escriba dentro de los notebooks, no la comparta y no entregue el archivo `.env` con los laboratorios.

**Modelo local (opcional).** Si quiere trabajar sin clave y sin costo, instale [Ollama](https://ollama.com/download), ábralo y, en una terminal, descargue el modelo del curso:

```
ollama pull qwen3:4b-instruct
```

Ocupa unos 2,5 GB y necesita unos 8 GB de memoria. En un portátil sin tarjeta gráfica funciona, pero es más lento que la API: úselo sobre todo en casa.

## 5. Comprobar que todo funciona

1. En VS Code, abra `entorno/verificar_entorno.ipynb`.
2. Haga clic en **Seleccionar kernel** (arriba a la derecha), elija **Python Environments** y luego el entorno `.venv` del curso.
3. Use **Ejecutar todo**. Cada comprobación debe mostrar ✓; si alguna muestra ✗, el mensaje dice qué hacer.

## 6. Problemas frecuentes

| Síntoma | Qué hacer |
| :--- | :--- |
| Windows no reconoce `python` | Use `py -3.13`, o reinstale Python marcando **Add python.exe to PATH** |
| **Seleccionar kernel** no muestra el entorno `.venv` | Compruebe que abrió la carpeta del curso. Luego, en la paleta de comandos, use **Developer: Reload Window** |
| Falla la instalación de librerías en la red de la empresa | Pruebe desde otra red; si no es posible, use el respaldo en Colab |
| La API responde con el error 401 | Revise el archivo `.env`: una sola línea, sin espacios, sin comillas y sin un `=` de más |
| Mac con procesador Intel | Algunas sesiones usan PyTorch, que ya no publica paquetes para Mac con procesador Intel. En esas sesiones use el respaldo en Colab |

## 7. Respaldo: Google Colab

Si no puede instalar software en su computador, los laboratorios también corren en [Google Colab](https://colab.research.google.com/). Suba el notebook con **Archivo › Subir notebook**, suba a la carpeta `/content` el .zip del laboratorio que entrega el docente y ejecute la primera celda. La clave de API se guarda en los **Secrets** de Colab con el nombre `ANTHROPIC_API_KEY`. En Colab no funciona el modelo local.
