"""Modelos preentrenados para el Laboratorio 4B (Sesión 4 de Sistemas Inteligentes).

Reúne lo que el notebook necesita para reconocer las cápsulas sin entrenar ningún modelo:
- las imágenes etiquetadas, una carpeta por clase;
- CLIP, que clasifica comparando cada imagen con una frase por clase;
- el LLM multimodal, a través del cliente común, con una instrucción fija;
- dos detectores: uno entrenado con las 80 clases de COCO (RT-DETRv2) y uno de vocabulario abierto (OWLv2);
- el pipeline del 4A, para comparar conteos;
- el registro de resultados en el CSV común del contrapunto.

Los modelos corren en la CPU. Los errores de configuración se muestran en español, en una caja roja, sin traza.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import os
import platform
import time
import unicodedata
import warnings
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

import cliente_llm
import figuras
import presentacion as p

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")   # en Windows, el caché copia en lugar de enlazar
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
warnings.filterwarnings("ignore", message="IProgress not found")   # sin ipywidgets, las barras de descarga son de texto

CARPETA_CAPSULAS = Path("imagenes") / "capsulas"
CARPETA_FOTOS = Path("imagenes") / "fotos"
CLASES_CASO = ("normal", "burbuja", "deforme", "mancha")
EXTENSIONES = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
LADO_VISTA = 448            # las imágenes se reducen a este lado para mostrarlas y para CLIP
FOTOS_CASO = {"principal": "capsulas_principal.jpg", "juntas": "capsulas_juntas.jpg", "limite": "capsulas_limite.jpg"}
NOMBRES_FOTOS = {"principal": "principal", "juntas": "juntas", "limite": "límite"}
# La configuración del pipeline del 4A que cuenta bien las fotos principal y juntas (la de la solución del 4A)
CONFIG_4A = {"canal": "saturacion", "suavizado": 5, "umbral": "otsu", "apertura": 7, "cierre": 0, "rellenar": True,
             "area_minima": 2500, "separar": True, "distancia_minima": 60}

# Cada modelo se fija en una versión exacta del repositorio de Hugging Face, para que todos descarguen lo mismo
MODELOS = {
    "clip": {"repo": "openai/clip-vit-base-patch32", "revision": "c237dc49a33fc61debc9276459120b7eac67e7ef",
             "mb": 609, "nombre": "CLIP ViT-B/32", "autor": "OpenAI", "licencia": "MIT",
             "uso": "clasificar con frases (sección 2)"},
    "owlv2": {"repo": "google/owlv2-base-patch16-ensemble", "revision": "cfd3195ba4ea9592eec887ded089f4c08eff231d",
              "mb": 622, "nombre": "OWLv2 base", "autor": "Google", "licencia": "Apache-2.0",
              "uso": "detectar objetos nombrados con texto (sección 4)"},
    "rtdetr": {"repo": "PekingU/rtdetr_v2_r18vd", "revision": "5650961749fa93567c0d46fc7f43ea4f9e914107",
               "mb": 81, "nombre": "RT-DETRv2 R18", "autor": "Baidu y Universidad de Pekín", "licencia": "Apache-2.0",
               "uso": "detectar las 80 clases de COCO (sección 4)"},
}

# La instrucción al LLM: la misma en todas las llamadas del caso
CONTEXTO_CASO = "La imagen muestra una cápsula blanda vista desde arriba; el gris alrededor es el fondo."
DEFINICIONES_CASO = {"normal": "sin defectos visibles", "burbuja": "tiene una burbuja de aire adentro",
                     "deforme": "su forma no es la alargada habitual", "mancha": "tiene un punto o una mancha oscura"}
RESPONDER = "Responde en la primera línea solo con el nombre de la clase, y en la segunda, en una frase, qué viste para decidir."
LADOS_GRABADOS = (112, 224, 448)
# La traducción literal de las frases de la redacción 1: el punto de partida del ejercicio de la sección 2.2
FRASES_TRADUCIDAS = {"normal": "a photo of a normal capsule", "burbuja": "a photo of a capsule with a bubble",
                     "deforme": "a photo of a deformed capsule", "mancha": "a photo of a capsule with a stain"}
SIN_RESPUESTA = figuras.SIN_RESPUESTA


class ErrorDeLaboratorio(Exception):
    """Un problema que la pareja puede corregir: se muestra en una caja roja, sin traza."""


def _amable(funcion):
    """Muestra los errores de configuración en una caja roja y devuelve None, en lugar de una traza larga."""
    def envoltura(*args, **kwargs):
        try:
            return funcion(*args, **kwargs)
        except ErrorDeLaboratorio as e:
            p.nota(str(e), "error", "Revise la configuración")
            return None
    envoltura.__doc__ = funcion.__doc__
    envoltura.__name__ = funcion.__name__
    return envoltura


def _normal(texto) -> str:
    """Minúsculas, sin tildes ni espacios sobrantes: «Burbuja » → «burbuja»."""
    t = unicodedata.normalize("NFD", str(texto).strip().lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def _n(valor, decimales: int = 0) -> str:
    """Número en formato español: espacio para los miles y coma decimal."""
    return f"{valor:,.{decimales}f}".replace(",", " ").replace(".", ",")


def _pct(fraccion) -> str:
    return f"{round(100 * fraccion)} %"


# ------------------------------------------------------------------ imágenes

@dataclass
class Imagen:
    ruta: Path
    clase: str
    nombre: str                 # clase/archivo
    _vista: object = field(default=None, repr=False)

    @property
    def imagen(self) -> Image.Image:
        """La imagen en color, enderezada según el celular y reducida a LADO_VISTA de lado."""
        if self._vista is None:
            try:
                im = ImageOps.exif_transpose(Image.open(self.ruta)).convert("RGB")
            except OSError:
                raise ErrorDeLaboratorio(f"No pude abrir «{self.ruta}» como imagen. Use fotos .jpg o .png.") from None
            im.thumbnail((LADO_VISTA, LADO_VISTA), Image.LANCZOS)
            self._vista = im
        return self._vista

    @property
    def miniatura(self) -> Image.Image:
        return self.imagen

    @property
    def huella(self) -> str:
        """Identifica el archivo original por su contenido: sirve para reconocer las respuestas grabadas."""
        return hashlib.sha256(self.ruta.read_bytes()).hexdigest()[:12]


@dataclass
class Conjunto:
    carpeta: Path
    clases: list
    imagenes: list

    def de_clase(self, clase) -> list:
        return [i for i in self.imagenes if i.clase == clase]

    @property
    def es_caso(self) -> bool:
        return self.carpeta.resolve() == CARPETA_CAPSULAS.resolve()

    def __repr__(self) -> str:
        return f"Conjunto({self.carpeta}: {len(self.imagenes)} imágenes, clases {', '.join(self.clases)})"


@_amable
def cargar_imagenes(carpeta=CARPETA_CAPSULAS, mostrar: bool = True) -> Conjunto:
    """Lee las imágenes de una carpeta con una subcarpeta por clase; el nombre de cada subcarpeta es su clase."""
    carpeta = Path(carpeta)
    if not carpeta.is_dir():
        raise ErrorDeLaboratorio(
            f"No encuentro la carpeta «{carpeta}». Revise el nombre: las imágenes del caso están en imagenes/capsulas/ "
            "y las suyas deben ir en mis_imagenes/, con una carpeta por clase.")
    subcarpetas = [d for d in sorted(carpeta.iterdir()) if d.is_dir() and not d.name.startswith((".", "_"))]
    if not subcarpetas:
        raise ErrorDeLaboratorio(
            f"Dentro de «{carpeta}» debe haber una carpeta por clase, por ejemplo {carpeta}/conforme/ y "
            f"{carpeta}/defecto/, con las imágenes de cada clase adentro.")
    if {d.name for d in subcarpetas} == set(CLASES_CASO):   # las clases del caso, en el orden del laboratorio
        subcarpetas.sort(key=lambda d: CLASES_CASO.index(d.name))
    clases, imagenes = [], []
    for d in subcarpetas:
        archivos = [f for f in sorted(d.iterdir()) if f.suffix.lower() in EXTENSIONES]
        if not archivos:
            raise ErrorDeLaboratorio(f"La carpeta de la clase «{d.name}» no tiene imágenes (.jpg o .png). "
                                     "Agregue al menos una o borre la carpeta.")
        clases.append(d.name)
        imagenes += [Imagen(f, d.name, f"{d.name}/{f.name}") for f in archivos]
    if len(clases) < 2:
        raise ErrorDeLaboratorio(f"«{carpeta}» tiene una sola clase ({clases[0]}): hacen falta al menos dos carpetas.")
    for img in imagenes:   # abre cada imagen ahora, para avisar enseguida si alguna no se puede leer
        img.imagen
    conjunto = Conjunto(carpeta, clases, imagenes)
    if mostrar:
        p.mostrar_tabla([{"clase": k, "imágenes": len(conjunto.de_clase(k))} for k in clases],
                        titulo=f"{len(imagenes)} imágenes en {carpeta}")
    return conjunto


def hay_imagenes_propias(carpeta="mis_imagenes") -> bool:
    """True si la carpeta tiene al menos dos subcarpetas con imágenes; si no, explica qué falta."""
    carpeta = Path(carpeta)
    clases = [d for d in carpeta.iterdir() if d.is_dir() and not d.name.startswith((".", "_"))] if carpeta.is_dir() else []
    con_imagenes = [d for d in clases if any(f.suffix.lower() in EXTENSIONES for f in d.iterdir())]
    if len(con_imagenes) >= 2:
        return True
    p.nota(f"Todavía no hay imágenes propias en {carpeta}/. Cree una carpeta por clase, por ejemplo "
           f"{carpeta}/conforme/ y {carpeta}/defecto/, copie sus imágenes y ejecute de nuevo.", "info")
    return False


@_amable
def galeria(conjunto, maximo_por_clase: int = 8, titulo: str = "") -> None:
    """Una fila de imágenes por clase."""
    if conjunto is None:
        raise ErrorDeLaboratorio("No hay imágenes cargadas: revise la celda donde se cargan.")
    figuras.galeria(conjunto, maximo_por_clase, titulo)


# ------------------------------------------------------------------ modelos locales

_CARGADOS: dict = {}


def _torch():
    try:
        import torch
    except ImportError:
        intel = platform.system() == "Darwin" and platform.machine() == "x86_64"
        raise ErrorDeLaboratorio(
            "No está instalada la librería torch, que necesitan CLIP y los detectores. "
            + ("En un Mac con procesador Intel no hay torch para Python 3.13: use el respaldo en Google Colab (sección 0)."
               if intel else "Ejecute la primera celda del notebook, o preparar.ipynb, y reinicie el kernel.")) from None
    return torch


def _clases_modelo(clave):
    from transformers import (AutoImageProcessor, AutoProcessor, CLIPModel, CLIPProcessor, Owlv2ForObjectDetection,
                              RTDetrV2ForObjectDetection)
    return {"clip": (CLIPModel, CLIPProcessor), "owlv2": (Owlv2ForObjectDetection, AutoProcessor),
            "rtdetr": (RTDetrV2ForObjectDetection, AutoImageProcessor)}[clave]


def descargado(clave) -> bool:
    """True si los pesos del modelo ya están en el caché de Hugging Face de este computador."""
    try:
        from huggingface_hub import try_to_load_from_cache
    except ImportError:
        return False
    info = MODELOS[clave]
    ruta = try_to_load_from_cache(info["repo"], "model.safetensors", revision=info["revision"])
    return isinstance(ruta, str)


def _cargar(clave, silencioso: bool = False):
    """Carga un modelo desde el caché; si no está, lo descarga una sola vez."""
    if clave in _CARGADOS:
        return _CARGADOS[clave]
    _torch()
    import huggingface_hub
    import transformers
    transformers.logging.set_verbosity_error()
    transformers.utils.logging.disable_progress_bar()        # la barra de «Loading weights» no informa nada
    huggingface_hub.utils.logging.set_verbosity_error()     # sin el aviso de descargar sin cuenta de Hugging Face
    info = MODELOS[clave]
    clase_modelo, clase_procesador = _clases_modelo(clave)
    inicio = time.perf_counter()
    local = descargado(clave)
    if not local and not silencioso:
        p.nota(f"{info['nombre']} no está descargado en este computador: se descarga ahora ({info['mb']} MB). "
               "Si está en el salón, la red puede tardar; la próxima vez quedará en el caché.", "aviso")
    try:
        modelo = clase_modelo.from_pretrained(info["repo"], revision=info["revision"], local_files_only=local)
        procesador = clase_procesador.from_pretrained(info["repo"], revision=info["revision"], local_files_only=local)
    except Exception as e:
        raise ErrorDeLaboratorio(f"No se pudo cargar {info['nombre']} ({type(e).__name__}). Revise la conexión a internet "
                                 "y ejecute preparar.ipynb; si el problema sigue, avise al docente.") from None
    modelo.eval()
    segundos = time.perf_counter() - inicio
    _CARGADOS[clave] = (modelo, procesador)
    if not silencioso:
        print(f"{info['nombre']} ({info['autor']}) cargado en {_n(segundos, 1)} s, en la CPU.")
    return _CARGADOS[clave]


def comprobar_modelos() -> bool:
    """Muestra qué modelos están descargados y si las librerías funcionan."""
    filas = []
    for clave, info in MODELOS.items():
        filas.append({"modelo": f"{info['nombre']} ({info['autor']})", "para qué": info["uso"],
                      "tamaño": f"{info['mb']} MB", "licencia": info["licencia"],
                      "descargado": "sí" if descargado(clave) else "no"})
    p.mostrar_tabla(filas, titulo="Modelos que corren en este computador")
    try:
        torch = _torch()
        import transformers
        version = f"torch {torch.__version__} · transformers {transformers.__version__}"
    except (ErrorDeLaboratorio, ImportError) as e:
        p.nota(str(e), "error", "Falta una librería")
        return False
    faltan = [MODELOS[k]["nombre"] for k in MODELOS if not descargado(k)]
    if faltan:
        p.nota(f"{version}. Faltan por descargar: {', '.join(faltan)}. Lo ideal es ejecutar preparar.ipynb antes de la "
               "clase; si no alcanzó, cada modelo se descargará la primera vez que se use.", "aviso")
        return False
    p.nota(f"{version}. Los tres modelos están descargados: CLIP y los detectores no necesitan internet.", "exito")
    return True


def descargar_modelos() -> bool:
    """Para preparar.ipynb: descarga los tres modelos y los prueba con una imagen."""
    total = 0.0
    for clave, info in MODELOS.items():
        ya = descargado(clave)
        print(f"{info['nombre']} ({info['mb']} MB): {'ya estaba descargado' if ya else 'descargando…'}")
        inicio = time.perf_counter()
        try:
            _cargar(clave, silencioso=True)
        except ErrorDeLaboratorio as e:
            p.nota(str(e), "error", f"No se pudo preparar {info['nombre']}")
            return False
        total += time.perf_counter() - inicio
        print(f"  ✓ listo en {_n(time.perf_counter() - inicio, 1)} s")
    conjunto = cargar_imagenes(mostrar=False)
    prueba = clasificar_clip(conjunto, {k: f"a photo of a {k} capsule" for k in CLASES_CASO}, "prueba",
                             mostrar=False, registrar=False)
    d = detectar_texto("principal", "a green capsule", 0.25, mostrar=False, registrar=False)
    if prueba is None or d is None:
        return False
    p.nota(f"Modelos listos. CLIP clasificó {len(conjunto.imagenes)} imágenes y OWLv2 encontró {d.conteo} cápsulas en una "
           f"foto. Tiempo total: {_n(total, 0)} s.", "exito", "✓ Preparación completa")
    return True


# ------------------------------------------------------------------ clasificaciones (CLIP y LLM)

@dataclass
class Clasificacion:
    metodo: str                     # "CLIP" o "LLM"
    nombre: str                     # la redacción o el tamaño de imagen
    clases: list
    imagenes: list
    asignadas: list                 # una clase por imagen, o None si no hubo respuesta válida
    frases: dict = field(default_factory=dict)          # CLIP: las frases de cada clase
    similitudes: np.ndarray | None = None               # CLIP: imagen × clase
    explicaciones: list = field(default_factory=list)   # LLM: qué dijo haber visto
    respuestas: list = field(default_factory=list)      # LLM: el texto completo
    metricas: dict = field(default_factory=dict)

    @property
    def reales(self) -> list:
        return [i.clase for i in self.imagenes]

    @property
    def aciertos(self) -> int:
        return sum(1 for r, a in zip(self.reales, self.asignadas) if r == a)

    @property
    def exactitud(self) -> float:
        return self.aciertos / len(self.imagenes) if self.imagenes else 0.0

    def por_clase(self) -> dict:
        return {k: sum(1 for r, a in zip(self.reales, self.asignadas) if r == k and a == k) for k in self.clases}

    def __repr__(self) -> str:
        return f"Clasificacion({self.metodo} · {self.nombre}: {self.aciertos} de {len(self.imagenes)})"


RESULTADOS: dict = {"clip": {}, "llm": {}, "repeticiones": {}, "deteccion": {}, "coco": {}, "4a": {}}
_REGISTRO: dict = {}   # (método, estrategia, instancia) → fila del CSV; repetir una corrida la reemplaza


def _validar_frases(frases, clases) -> dict:
    """Devuelve {clase: [frases]} en el orden de las clases, o explica qué corregir."""
    if not isinstance(frases, dict):
        raise ErrorDeLaboratorio('Las frases van en un diccionario, una entrada por clase: {"normal": "a photo of …", …}.')
    por_clase = {}
    for clave, valor in frases.items():
        clase = next((k for k in clases if _normal(k) == _normal(clave)), None)
        if clase is None:
            raise ErrorDeLaboratorio(f"«{clave}» no es una de las clases ({', '.join(clases)}). Revise cómo la escribió.")
        lista = [valor] if isinstance(valor, str) else list(valor) if isinstance(valor, (list, tuple)) else None
        if lista is None or not all(isinstance(x, str) for x in lista):
            raise ErrorDeLaboratorio(f"La frase de la clase «{clase}» debe ir entre comillas, o ser una lista de frases "
                                     "entre corchetes.")
        lista = [x.strip() for x in lista]
        if not lista or not all(lista):
            raise ErrorDeLaboratorio(f"La clase «{clase}» no tiene ninguna frase: escriba al menos una entre las comillas.")
        por_clase[clase] = lista
    faltan = [k for k in clases if k not in por_clase]
    if faltan:
        raise ErrorDeLaboratorio(f"La clase «{faltan[0]}» no tiene ninguna frase. Cada clase necesita al menos una.")
    return {k: por_clase[k] for k in clases}


def _vectores_imagenes(conjunto):
    """Los vectores de CLIP de cada imagen: se calculan una vez por conjunto y se guardan."""
    clave = ("imagenes", tuple(str(i.ruta) for i in conjunto.imagenes))
    if clave not in _CARGADOS:
        torch = _torch()
        modelo, procesador = _cargar("clip")
        inicio = time.perf_counter()
        vectores = []
        with torch.inference_mode():
            for k in range(0, len(conjunto.imagenes), 16):
                lote = [i.imagen for i in conjunto.imagenes[k:k + 16]]
                v = modelo.get_image_features(**procesador(images=lote, return_tensors="pt")).pooler_output
                vectores.append(v / v.norm(dim=-1, keepdim=True))
        _CARGADOS[clave] = (torch.cat(vectores).numpy(), time.perf_counter() - inicio)
    return _CARGADOS[clave]


def _vectores_frases(frases_por_clase: dict) -> np.ndarray:
    """Un vector por clase: el de su frase, o el promedio de los de sus frases (un conjunto de frases)."""
    torch = _torch()
    modelo, procesador = _cargar("clip")
    filas = []
    with torch.inference_mode():
        for lista in frases_por_clase.values():
            v = modelo.get_text_features(**procesador(text=lista, return_tensors="pt", padding=True,
                                                      truncation=True)).pooler_output
            v = v / v.norm(dim=-1, keepdim=True)
            m = v.mean(0)
            filas.append((m / m.norm()).numpy())
    return np.stack(filas)


@_amable
def clasificar_clip(conjunto, frases: dict, nombre: str = "", mostrar: bool = True, registrar: bool = True):
    """Clasifica cada imagen con la clase cuya frase está más cerca en el espacio de CLIP."""
    if conjunto is None:
        raise ErrorDeLaboratorio("No hay imágenes cargadas: revise la celda donde se cargan.")
    if frases is None:   # la celda ya mostró por qué no hay frases (por ejemplo, una plantilla sin {})
        return None
    por_clase = _validar_frases(frases, conjunto.clases)
    repetidas = {f for k, l in por_clase.items() for f in l if sum(f in l2 for l2 in por_clase.values()) > 1}
    if repetidas:
        p.nota(f"Dos clases comparten la frase «{next(iter(repetidas))}»: CLIP no podrá distinguirlas.", "aviso")
    imagenes, t_imagenes = _vectores_imagenes(conjunto)
    inicio = time.perf_counter()
    texto = _vectores_frases(por_clase)
    t_texto = time.perf_counter() - inicio
    sim = imagenes @ texto.T
    asignadas = [conjunto.clases[j] for j in sim.argmax(1)]
    n = len(conjunto.imagenes)
    c = Clasificacion("CLIP", nombre or f"redacción {len(RESULTADOS['clip']) + 1}", list(conjunto.clases),
                      list(conjunto.imagenes), asignadas,
                      frases={k: (v[0] if len(v) == 1 else v) for k, v in por_clase.items()}, similitudes=sim,
                      metricas={"proveedor": "local", "modelo": MODELOS["clip"]["repo"],
                                "segundos_por_imagen": (t_imagenes + t_texto) / n})
    if registrar:
        RESULTADOS["clip"][c.nombre] = c
        for img, a in zip(c.imagenes, c.asignadas):
            _registrar(_fila("clasificar cápsulas" if conjunto.es_caso else "clasificar imágenes propias", img.nombre,
                             "preentrenado", f"CLIP · {c.nombre}", "local", MODELOS["clip"]["repo"], a == img.clase, a,
                             tiempo_s=round(c.metricas["segundos_por_imagen"], 4),
                             notas="frases: " + json.dumps(c.frases, ensure_ascii=False)))
    if mostrar:
        figuras.matriz(c)
        print(f"Tiempo de CLIP en la CPU: {_n(1000 * c.metricas['segundos_por_imagen'], 0)} ms por imagen.")
    return c


@_amable
def frases_con_plantillas(plantillas, etiquetas: dict) -> dict | None:
    """Combina cada plantilla con la etiqueta de cada clase: un conjunto de frases por clase."""
    if isinstance(plantillas, str):
        plantillas = [plantillas]
    if not isinstance(plantillas, (list, tuple)) or not plantillas or not all(isinstance(t, str) for t in plantillas):
        raise ErrorDeLaboratorio('PLANTILLAS es una lista de frases entre comillas, por ejemplo ["a photo of a {}."].')
    sin_hueco = [t for t in plantillas if t.count("{}") != 1]
    if sin_hueco:
        raise ErrorDeLaboratorio(f"La plantilla «{sin_hueco[0]}» debe tener una vez {{}}, donde va la etiqueta de la clase.")
    if not isinstance(etiquetas, dict) or not all(isinstance(v, str) and v.strip() for v in etiquetas.values()):
        raise ErrorDeLaboratorio('ETIQUETAS es un diccionario con una etiqueta entre comillas por clase: {"normal": "…", …}.')
    con_plantilla = [v for v in etiquetas.values() if _normal(v).startswith(("a photo", "a picture", "una foto"))]
    if con_plantilla:
        p.nota(f"La etiqueta «{con_plantilla[0]}» ya trae el comienzo de una plantilla: escriba solo la descripción, por "
               "ejemplo «smooth elongated capsule», porque la plantilla pone el resto.", "aviso")
    return {k: [t.format(v.strip()) for t in plantillas] for k, v in etiquetas.items()}


def mostrar_frases(c) -> None:
    """Las frases de una clasificación de CLIP, como tabla."""
    if c is None:
        return
    p.mostrar_tabla([{"clase": k, "frase o frases": v if isinstance(v, str) else " | ".join(v)} for k, v in c.frases.items()],
                    titulo=f"Frases de CLIP · {c.nombre}")


@_amable
def mostrar_similitudes(c, imagen: str | int = 0) -> None:
    """La similitud de una imagen con la frase de cada clase."""
    if c is None or c.similitudes is None:
        raise ErrorDeLaboratorio("Primero ejecute la celda que clasifica con CLIP.")
    if isinstance(imagen, str):
        nombres = [i.nombre for i in c.imagenes]
        if imagen not in nombres:
            raise ErrorDeLaboratorio(f"No encuentro «{imagen}». Escríbala como clase/archivo, por ejemplo «burbuja/burbuja_03.jpg».")
        imagen = nombres.index(imagen)
    figuras.similitudes(c, imagen)


@_amable
def mostrar_errores(c, maximo: int = 32) -> None:
    """La galería de errores de una clasificación."""
    if c is None:
        raise ErrorDeLaboratorio("Primero ejecute la celda que clasifica.")
    figuras.galeria_errores(c, maximo)


def mostrar_redacciones() -> None:
    """Todas las redacciones de CLIP probadas en el caso, con su exactitud total y por clase."""
    filas = []
    for c in RESULTADOS["clip"].values():
        if not c.imagenes or c.clases != list(CLASES_CASO):
            continue
        fila = {"redacción": c.nombre, "exactitud": f"{c.aciertos} de {len(c.imagenes)} ({_pct(c.exactitud)})"}
        fila.update({k: f"{v} de {len(c.imagenes) // len(c.clases)}" for k, v in c.por_clase().items()})
        filas.append(fila)
    if filas:
        p.mostrar_tabla(filas, titulo="Redacciones de CLIP probadas (las 32 cápsulas del caso)")
    else:
        p.nota("Todavía no hay redacciones registradas.", "info")


def comprobar_redaccion(c, base, partida: dict | None = None) -> None:
    """Compara una redacción con la anterior y orienta el siguiente intento. No califica."""
    if c is None or base is None:
        return
    if partida is not None and all(_normal(c.frases.get(k)) == _normal(v) for k, v in partida.items() if isinstance(v, str)):
        p.nota("Son las frases de partida. Cámbielas por su propia redacción: describa en inglés cómo se ve cada clase.",
               "aviso", "Todavía no hay una redacción suya")
        return
    azar = 1 / len(c.clases)
    lineas = [f"{c.nombre}: {c.aciertos} de {len(c.imagenes)} ({_pct(c.exactitud)}), frente a {base.aciertos} de "
              f"{len(base.imagenes)} ({_pct(base.exactitud)}) con la {base.nombre}."]
    diferencia = c.aciertos - base.aciertos
    if abs(diferencia) <= 2:
        lineas.append(f"Una diferencia de {abs(diferencia)} imagen(es) entre 32 no es concluyente: cada imagen vale 3 puntos.")
    if c.exactitud <= azar + 0.07:
        lineas.append(f"Está cerca del azar ({_pct(azar)}): mire en la matriz si casi todo cae en una sola columna.")
    vacias = [k for k, v in c.por_clase().items() if v == 0]
    if vacias:
        lineas.append(f"Ninguna imagen de {', '.join('«' + k + '»' for k in vacias)} quedó bien. En una clase con defecto, "
                      "describa lo que la distingue (forma, tamaño, color). Si después de dos intentos sigue en cero, siga "
                      "adelante: que CLIP no distinga una clase también es un resultado, y se analiza.")
    texto = " ".join(_normal(f) for v in c.frases.values() for f in ([v] if isinstance(v, str) else v))
    if any(w in f" {texto} " for w in (" una ", " con ", " capsula", " foto ")):
        lineas.append("Sus frases parecen estar en español; CLIP aprendió sobre todo con textos en inglés.")
    p.nota("\n".join(lineas), "exito" if c.aciertos > base.aciertos else "info", f"Comparación con la {base.nombre}")


# ------------------------------------------------------------------ el LLM multimodal

def instruccion(clases, definiciones: dict | None = None, contexto: str | None = None) -> str:
    """La instrucción al LLM: el contexto, las clases con su definición y el formato de la respuesta."""
    definiciones = definiciones or {}
    lineas = []
    for i, k in enumerate(clases):
        fin = "." if i == len(clases) - 1 else ";"
        d = definiciones.get(k)
        lineas.append(f"- {k}: {d}{fin}" if d else f"- {k}{fin}")
    cabeza = f"{contexto} Clasifícala en una de estas clases:" if contexto else "Clasifica la imagen en una de estas clases:"
    return cabeza + "\n" + "\n".join(lineas) + "\n" + RESPONDER


def instruccion_caso() -> str:
    return instruccion(CLASES_CASO, DEFINICIONES_CASO, CONTEXTO_CASO)


def mostrar_instruccion(texto: str | None = None) -> None:
    p.mostrar_conversacion([{"rol": "user", "contenido": texto or instruccion_caso()}],
                           titulo="La instrucción que recibe el LLM con cada imagen", abierta=True)


def leer_respuesta(texto: str, clases) -> tuple:
    """La clase de la primera línea, solo si es exactamente una de las clases; si no, None (sin adivinar)."""
    lineas = [l.strip() for l in (texto or "").strip().splitlines() if l.strip()]
    if not lineas:
        return None, ""
    primera = _normal(lineas[0]).strip("*_`#.:;,!¡¿?\"'«» ")
    clase = next((k for k in clases if _normal(k) == primera), None)
    return clase, " ".join(lineas[1:]).strip("*_ ")[:300]


def tokens_imagen(ancho: int, alto: int) -> int:
    """Tokens de una imagen en Claude, según su documentación: un token por cada parche de 28 × 28 píxeles."""
    return math.ceil(ancho / 28) * math.ceil(alto / 28)


def _bytes_llm(img: Imagen, lado: int) -> tuple:
    """La imagen reducida a «lado» píxeles en su lado mayor, como JPEG; también devuelve su ancho y su alto."""
    im = ImageOps.exif_transpose(Image.open(img.ruta)).convert("RGB")
    escala = lado / max(im.size)
    tamano = (max(1, round(im.width * escala)), max(1, round(im.height * escala)))
    im = im.resize(tamano, Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=90)
    return buf.getvalue(), tamano


def _validar_lado(lado) -> int:
    if isinstance(lado, bool) or not isinstance(lado, (int, float)):
        raise ErrorDeLaboratorio(f"El tamaño debe ser un número de píxeles, sin comillas, por ejemplo 224 (escribió {lado!r}).")
    lado = int(lado)
    if not 28 <= lado <= 1568:
        raise ErrorDeLaboratorio("El tamaño debe estar entre 28 y 1568 píxeles; pruebe 112, 224 o 448.")
    return lado


@_amable
def clasificar_llm(llm, conjunto, lado: int = 224, definiciones: dict | None = None, contexto: str | None = None,
                   experimento: str = "clase", nombre: str | None = None, mostrar: bool = True):
    """Envía cada imagen al LLM con la misma instrucción y arma la clasificación con sus métricas."""
    if llm is None:
        raise ErrorDeLaboratorio("Primero cree el cliente del LLM, en la sección 0.2.")
    if conjunto is None:
        raise ErrorDeLaboratorio("No hay imágenes cargadas: revise la celda donde se cargan.")
    lado = _validar_lado(lado)
    if conjunto.es_caso:
        definiciones, contexto = DEFINICIONES_CASO, CONTEXTO_CASO
        if lado > LADO_VISTA:
            p.nota(f"Las imágenes del caso miden {LADO_VISTA} píxeles: ampliarlas sube los tokens sin agregar detalle.", "aviso")
    texto = instruccion(conjunto.clases, definiciones, contexto)
    previa = RESULTADOS["llm"].get(lado) if conjunto.es_caso and experimento == "clase" else None
    if previa is not None and previa.metricas.get("proveedor") == llm.proveedor:
        # Ya se clasificaron estas imágenes con este tamaño en esta sesión: no se paga otra vez
        if mostrar:
            print(f"Las cápsulas de {lado} px ya se clasificaron en esta sesión; se muestra ese resultado. "
                  "Para ver si el LLM responde distinto, use la sección 6.")
            figuras.matriz(previa)
            resumen_costo(previa)
        return previa
    etiquetas = [f"4b/{experimento}/{lado}px/{img.nombre}" for img in conjunto.imagenes]
    if llm.proveedor == "grabado":
        grabadas = getattr(llm, "_grabaciones", {})
        faltan = [e for e in etiquetas if e not in grabadas]
        if len(faltan) == len(etiquetas):
            lados = sorted({int(e.split("/")[2][:-2]) for e in grabadas if e.startswith(f"4b/{experimento}/")})
            raise ErrorDeLaboratorio(
                f"No hay respuestas grabadas para imágenes de {lado} píxeles"
                + (f": en modo grabado use {', '.join(map(str, lados[:-1]))} o {lados[-1]}." if len(lados) > 1
                   else f": en modo grabado use {lados[0]}." if lados else ".")
                + " Para probar otros tamaños o imágenes propias, configure una clave de API o un modelo local.")
        if faltan:
            p.nota(f"Faltan {len(faltan)} respuestas grabadas; esas imágenes se omiten.", "aviso")
    asignadas, explicaciones, respuestas, usadas, medidas = [], [], [], [], []
    inicio = time.perf_counter()
    n = len(conjunto.imagenes)
    for k, (img, etiqueta) in enumerate(zip(conjunto.imagenes, etiquetas), 1):
        if llm.proveedor == "grabado" and etiqueta not in getattr(llm, "_grabaciones", {}):
            continue
        datos, tamano = _bytes_llm(img, lado)
        mensaje = cliente_llm.mensaje_con_imagen(texto, datos, "image/jpeg", id=f"{img.nombre}@{lado}px#{img.huella}")
        try:
            r = llm.completar([mensaje], etiqueta=etiqueta, max_tokens_respuesta=200)
        except (cliente_llm.PresupuestoAgotado, cliente_llm.ErrorLLM) as e:
            p.nota(f"{e}\nSe muestran las {len(usadas)} imágenes clasificadas antes del error.", "error", "El LLM se detuvo")
            break
        if not r.disponible:
            continue
        clase, explicacion = leer_respuesta(r.texto, conjunto.clases)
        asignadas.append(clase)
        explicaciones.append(explicacion)
        respuestas.append(r.texto)
        usadas.append(img)
        medidas.append({"tokens_entrada": r.tokens_entrada, "tokens_salida": r.tokens_salida,
                        "tokens_razonamiento": r.tokens_razonamiento, "costo_usd": r.costo_usd or 0.0,
                        "segundos": r.segundos, "tamano": tamano, "proveedor": r.proveedor, "modelo": r.modelo,
                        "grabada": r.grabada, "fecha": r.fecha})
        if mostrar and k % 8 == 0 and k < n and not r.grabada:
            print(f"  {k} de {n} imágenes · {_n(time.perf_counter() - inicio, 0)} s")
    if not usadas:
        raise ErrorDeLaboratorio("El LLM no clasificó ninguna imagen.")
    m0 = medidas[0]
    proveedor = m0["proveedor"]
    metricas = {"proveedor": proveedor, "modelo": m0["modelo"], "lado": lado, "instruccion": texto,
                "grabada": m0["grabada"], "fecha": m0["fecha"][:10],
                "tokens_entrada": sum(x["tokens_entrada"] for x in medidas),
                "tokens_salida": sum(x["tokens_salida"] for x in medidas),
                "tokens_razonamiento": sum(x["tokens_razonamiento"] for x in medidas),
                "costo_usd": sum(x["costo_usd"] for x in medidas), "segundos": sum(x["segundos"] for x in medidas),
                "tokens_formula": [tokens_imagen(*x["tamano"]) for x in medidas], "por_imagen": medidas}
    c = Clasificacion("LLM", nombre or f"imágenes de {lado} px", list(conjunto.clases), usadas, asignadas,
                      explicaciones=explicaciones, respuestas=respuestas, metricas=metricas)
    if conjunto.es_caso and experimento == "clase":
        RESULTADOS["llm"][lado] = c
    elif experimento.startswith("repeticion"):
        RESULTADOS["repeticiones"][(experimento, lado)] = c
    else:
        RESULTADOS["llm"][(str(conjunto.carpeta), lado)] = c
    temperatura = "la del proveedor (el SDK de Anthropic no la expone)" if "claude" in str(m0["modelo"]) else "0"
    for img, a, e, x in zip(usadas, asignadas, explicaciones, medidas):
        _registrar(_fila("clasificar cápsulas" if conjunto.es_caso else "clasificar imágenes propias", img.nombre, "llm",
                         f"LLM · {lado} px" + ("" if experimento == "clase" else f" · {experimento}"), proveedor,
                         x["modelo"], a == img.clase, a or SIN_RESPUESTA, llamadas=1, tokens_entrada=x["tokens_entrada"],
                         tokens_salida=x["tokens_salida"], tokens_razonamiento=x["tokens_razonamiento"],
                         costo_usd=round(x["costo_usd"], 7), tiempo_s=x["segundos"],
                         notas=f"lado {lado} px; razonamiento desactivado; temperatura: {temperatura}; "
                               f"fecha de la respuesta {x['fecha'][:10]}; explicación: {e}"))
    if mostrar:
        figuras.matriz(c)
        resumen_costo(c)
    return c


def probar_tamanos(llm, conjunto, lados) -> None:
    """Clasifica con cada tamaño de la lista y muestra la comparación de tokens, exactitud y costo."""
    if isinstance(lados, (int, float)) and not isinstance(lados, bool):
        lados = [lados]
    if not isinstance(lados, (list, tuple)) or not lados:
        p.nota("Escriba entre los corchetes el tamaño que quiere probar, por ejemplo [448], y ejecute de nuevo.", "info")
        return
    for lado in lados:
        clasificar_llm(llm, conjunto, lado=lado)
    comparar_tamanos()


def resumen_costo(c) -> None:
    """Tokens, costo y tiempo de una clasificación con el LLM."""
    if c is None:
        return
    m, n = c.metricas, len(c.imagenes)
    origen = (f"respuestas grabadas el {m['fecha']} con {m['modelo']}: las cifras son las de esa corrida"
              if m["grabada"] else f"{m['proveedor']} · {m['modelo']}")
    invalidas = sum(1 for a in c.asignadas if a is None)
    p.nota(f"{n} imágenes de {m['lado']} px · {origen}.\n"
           f"Tokens de entrada: {_n(m['tokens_entrada'])} ({_n(m['tokens_entrada'] / n)} por imagen) · de salida: "
           f"{_n(m['tokens_salida'])}.\n"
           f"Costo: US${_n(m['costo_usd'], 5)} en total, US${_n(m['costo_usd'] / n, 6)} por imagen, unos "
           f"US${_n(1000 * m['costo_usd'] / n, 2)} por cada 1000 imágenes.\n"
           f"Tiempo: {_n(m['segundos'] / n, 1)} s por imagen, esperando la respuesta."
           + (f"\nSin respuesta válida: {invalidas} (la primera línea no era una de las clases)." if invalidas else ""),
           "neutro", "Lo que costó")


def comparar_tamanos() -> None:
    """Tokens medidos frente a la fórmula de la documentación de Claude, exactitud y costo, por tamaño de imagen."""
    filas = []
    for lado in sorted(k for k in RESULTADOS["llm"] if isinstance(k, int)):
        c = RESULTADOS["llm"][lado]
        m, n = c.metricas, len(c.imagenes)
        claude = "claude" in str(m["modelo"])
        formula = m["tokens_formula"][0] if claude else None
        medidos = m["tokens_entrada"] / n
        filas.append({"lado (px)": lado,
                      "tokens de la imagen, por la fórmula": _n(formula) if claude else "— (otra fórmula)",
                      "tokens de entrada medidos, por imagen": _n(medidos),
                      "diferencia: la instrucción": _n(medidos - formula) if claude else "—",
                      "exactitud": f"{c.aciertos} de {n} ({_pct(c.exactitud)})",
                      "US$ por 1000 imágenes": _n(1000 * m["costo_usd"] / n, 2),
                      "s por imagen": _n(m["segundos"] / n, 1)})
    if not filas:
        p.nota("Todavía no hay clasificaciones con el LLM.", "info")
        return
    p.mostrar_tabla(filas, titulo="El LLM según el tamaño de la imagen")
    print("Fórmula de la documentación de Claude: ⌈ancho/28⌉ × ⌈alto/28⌉ tokens por imagen.")


@_amable
def repetir_llm(llm, conjunto, lado: int = 224, repeticiones: int = 2) -> None:
    """Vuelve a enviar las mismas imágenes con la misma instrucción y muestra qué respuestas cambian."""
    if not isinstance(repeticiones, int) or not 1 <= repeticiones <= 5:
        raise ErrorDeLaboratorio("REPETICIONES debe ser un número entero de 1 a 5.")
    lado = _validar_lado(lado)
    if llm is not None and llm.proveedor == "grabado":
        grabadas = getattr(llm, "_grabaciones", {})
        disponibles = sum(1 for k in range(1, 6) if any(e.startswith(f"4b/repeticion{k}/{lado}px/") for e in grabadas))
        if disponibles == 0:
            raise ErrorDeLaboratorio(f"Con respuestas grabadas no hay repeticiones de imágenes de {lado} píxeles: use 224, "
                                     "o configure una clave de API o un modelo local.")
        if repeticiones > disponibles:
            p.nota(f"Con respuestas grabadas solo hay {disponibles} repeticiones; se muestran esas. Con la API o un modelo "
                   "local puede pedir más.", "info")
            repeticiones = disponibles
    corridas = []
    primera = RESULTADOS["llm"].get(lado) or clasificar_llm(llm, conjunto, lado, mostrar=False)
    if primera is None:
        return
    corridas.append(primera)
    for k in range(1, repeticiones + 1):
        c = clasificar_llm(llm, conjunto, lado, experimento=f"repeticion{k}", nombre=f"{lado} px · repetición {k}",
                           mostrar=False)
        if c is None:
            break
        corridas.append(c)
    respuestas = [{i.nombre: a for i, a in zip(c.imagenes, c.asignadas)} for c in corridas]
    comunes = [i for i in primera.imagenes if all(i.nombre in r for r in respuestas)]
    cambian = [i for i in comunes if len({r[i.nombre] for r in respuestas}) > 1]
    filas = [{"imagen": i.nombre, "real": i.clase,
              **{f"corrida {j + 1}": r[i.nombre] or SIN_RESPUESTA for j, r in enumerate(respuestas)}} for i in cambian]
    exactitudes = ", ".join(f"{c.aciertos} de {len(c.imagenes)}" for c in corridas)
    p.nota(f"{len(corridas)} corridas con la misma instrucción y las mismas imágenes de {lado} px. Aciertos por corrida: "
           f"{exactitudes}. {len(cambian)} de {len(comunes)} imágenes recibieron más de una clase.",
           "neutro", "Variabilidad del LLM")
    if filas:
        p.mostrar_tabla(filas, titulo="Imágenes cuya clase cambió entre corridas")


# ------------------------------------------------------------------ detectores

@dataclass
class Deteccion:
    foto: str
    imagen: Image.Image
    descripcion: str
    cajas: np.ndarray            # (x0, y0, x1, y1) en píxeles de la foto
    puntajes: np.ndarray
    etiquetas: list
    segundos: float
    comparacion: dict | None = None

    @property
    def conteo(self) -> int:
        return len(self.cajas)

    def estado_cajas(self) -> list:
        if self.comparacion is None:
            return ["sin referencia"] * self.conteo
        c = self.comparacion
        return ["correcta" if i in c["correctas"] else "junta" if i in c["juntas"] else "sobrante"
                for i in range(self.conteo)]

    def resumen(self) -> str:
        if self.comparacion is None:
            return f"{self.conteo} cajas"
        c = self.comparacion
        perdidas = len(c["perdidas"])
        return (f"{self.conteo} cajas: {len(c['correctas'])} con una cápsula, {len(c['juntas'])} con dos o más, "
                f"{len(c['sobrantes'])} de más; {perdidas} {'cápsula perdida' if perdidas == 1 else 'cápsulas perdidas'}")

    @property
    def exacta(self) -> bool:
        c = self.comparacion
        return bool(c) and len(c["correctas"]) == c["cantidad"] and not (c["juntas"] or c["sobrantes"] or c["perdidas"])


def _ruta_foto(foto) -> Path:
    nombre = FOTOS_CASO.get(_normal(foto), str(foto))
    for ruta in (Path(nombre), CARPETA_FOTOS / nombre):
        if ruta.is_file():
            return ruta
    raise ErrorDeLaboratorio(f"No encuentro la foto «{foto}». Use «principal», «juntas» o «limite», o la ruta de una foto suya.")


def _referencia(ruta: Path) -> dict | None:
    archivo = CARPETA_FOTOS / "referencias.json"
    if not archivo.exists():
        return None
    return json.loads(archivo.read_text(encoding="utf-8")).get(ruta.name)


def _abrir_foto(ruta: Path) -> Image.Image:
    im = ImageOps.exif_transpose(Image.open(ruta)).convert("RGB")
    im.thumbnail((1000, 1000), Image.LANCZOS)
    return im


def _comparar_cajas(cajas, ref) -> dict | None:
    """Cada cápsula de la referencia va a la caja que la contiene con el centro más cercano.

    Una caja sin cápsula propia que encierra dos o más cápsulas cuenta como «con dos o más»; si no encierra ninguna,
    o solo repite una caja vecina, es una caja «de más»."""
    if ref is None:
        return None
    asignadas, perdidas = {}, []
    dentro_de = {i: 0 for i in range(len(cajas))}
    for cx, cy in ref["centros"]:
        dentro = [i for i, (x0, y0, x1, y1) in enumerate(cajas) if x0 <= cx <= x1 and y0 <= cy <= y1]
        for i in dentro:
            dentro_de[i] += 1
        if not dentro:
            perdidas.append((cx, cy))
            continue
        i = min(dentro, key=lambda i: ((cajas[i][0] + cajas[i][2]) / 2 - cx) ** 2 + ((cajas[i][1] + cajas[i][3]) / 2 - cy) ** 2)
        asignadas.setdefault(i, []).append((cx, cy))
    juntas = {i: len(v) for i, v in asignadas.items() if len(v) > 1}
    juntas.update({i: n for i, n in dentro_de.items() if i not in asignadas and n > 1})
    return {"cantidad": ref["cantidad"], "correctas": [i for i, v in asignadas.items() if len(v) == 1],
            "juntas": juntas, "sobrantes": [i for i in range(len(cajas)) if i not in asignadas and i not in juntas],
            "perdidas": perdidas}


def _suprimir(cajas: np.ndarray, puntajes: np.ndarray, iou_maximo: float = 0.3) -> list:
    """Supresión de no máximos: de las cajas que se solapan mucho, se queda la de mayor confianza."""
    quedan = []
    for i in np.argsort(-puntajes):
        x0, y0, x1, y1 = cajas[i]
        repetida = False
        for j in quedan:
            a0, b0, a1, b1 = cajas[j]
            inter = max(0, min(x1, a1) - max(x0, a0)) * max(0, min(y1, b1) - max(y0, b0))
            union = (x1 - x0) * (y1 - y0) + (a1 - a0) * (b1 - b0) - inter
            if union > 0 and inter / union > iou_maximo:
                repetida = True
                break
        if not repetida:
            quedan.append(int(i))
    return quedan


def _validar_umbral(umbral) -> float:
    if isinstance(umbral, tuple) and len(umbral) == 2:
        raise ErrorDeLaboratorio("En el código, los decimales se escriben con punto, no con coma: por ejemplo 0.25.")
    if isinstance(umbral, bool) or not isinstance(umbral, (int, float)) or not 0 < umbral < 1:
        raise ErrorDeLaboratorio(f"El umbral de confianza va entre 0 y 1, sin comillas, por ejemplo 0.25 (escribió {umbral!r}).")
    return float(umbral)


def _crudas_owlv2(ruta: Path, texto: str):
    """Todas las cajas candidatas de OWLv2 para un texto, con su confianza. Se guardan para no repetir el cálculo."""
    clave = ("owlv2", str(ruta), texto)
    if clave not in _CARGADOS:
        torch = _torch()
        modelo, procesador = _cargar("owlv2")
        imagen = _abrir_foto(ruta)
        inicio = time.perf_counter()
        with torch.inference_mode():
            salida = modelo(**procesador(text=[[texto]], images=imagen, return_tensors="pt"))
        lado = max(imagen.size)   # OWLv2 completa la foto hasta un cuadrado: las cajas se escalan a ese lado
        res = procesador.post_process_grounded_object_detection(salida, threshold=0.02,
                                                                target_sizes=torch.tensor([[lado, lado]]))[0]
        _CARGADOS[clave] = (imagen, res["boxes"].numpy(), res["scores"].numpy(), time.perf_counter() - inicio)
    return _CARGADOS[clave]


@_amable
def detectar_texto(foto="principal", texto: str = "a capsule", umbral: float = 0.3, mostrar: bool = True,
                   registrar: bool = True):
    """OWLv2: busca en la foto los objetos que describe el texto y deja las cajas con confianza ≥ umbral."""
    if not isinstance(texto, str) or not texto.strip():
        raise ErrorDeLaboratorio('Escriba entre comillas qué buscar, por ejemplo "a capsule".')
    umbral = _validar_umbral(umbral)
    ruta = _ruta_foto(foto)
    imagen, cajas, puntajes, segundos = _crudas_owlv2(ruta, texto.strip())
    filtro = puntajes >= umbral
    cajas, puntajes = cajas[filtro], puntajes[filtro]
    orden = _suprimir(cajas, puntajes) if len(cajas) else []
    cajas, puntajes = cajas[orden], puntajes[orden]
    d = Deteccion(ruta.name, imagen, f"OWLv2 · «{texto.strip()}» · umbral {umbral:g} · {ruta.name}", cajas.reshape(-1, 4),
                  puntajes, [""] * len(cajas), segundos, _comparar_cajas(cajas.reshape(-1, 4).tolist(), _referencia(ruta)))
    if registrar:
        RESULTADOS["deteccion"][ruta.name] = d
        _registrar(_fila("contar cápsulas", ruta.name, "preentrenado", f"OWLv2 · «{texto.strip()}» · umbral {umbral:g}",
                         "local", MODELOS["owlv2"]["repo"], d.exacta, d.resumen(), tiempo_s=round(segundos, 2)))
    if mostrar:
        figuras.cajas(d)
        _informe_deteccion(d)
    return d


def _informe_deteccion(d: Deteccion) -> None:
    tiempo = f" OWLv2 tardó {_n(d.segundos, 1)} s en la CPU."
    if d.comparacion is None:
        p.nota(d.resumen() + "." + tiempo, "info")
    elif d.exacta:
        p.nota(f"✓ {d.resumen()}: las {d.comparacion['cantidad']} cápsulas, cada una en su caja.{tiempo}", "exito")
    elif d.conteo == 0:
        p.nota(f"Ninguna caja supera el umbral.{tiempo} Baje el umbral o cambie el texto; la tabla de abajo muestra hasta "
               "dónde llega la confianza con este texto.", "aviso")
    else:
        p.nota(d.resumen() + "." + tiempo, "aviso")


@_amable
def barrido_umbral(foto="principal", texto: str = "a capsule",
                   umbrales=(0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5)) -> None:
    """Cuántas cajas quedan con cada umbral, para el mismo texto: el cálculo del modelo se hace una sola vez."""
    ruta = _ruta_foto(foto)
    filas = []
    for u in umbrales:
        d = detectar_texto(ruta, texto, u, mostrar=False, registrar=False)
        if d is None:
            return
        fila = {"umbral": u, "cajas": d.conteo}
        if d.comparacion:
            c = d.comparacion
            fila.update({"con una cápsula": len(c["correctas"]), "con dos o más": len(c["juntas"]),
                         "de más": len(c["sobrantes"]), "cápsulas perdidas": len(c["perdidas"])})
        filas.append(fila)
    maximo = float(_crudas_owlv2(ruta, texto.strip())[2].max(initial=0))
    p.mostrar_tabla(filas, titulo=f"«{texto.strip()}» en {ruta.name}: la caja más confiable tiene {maximo:.2f}")


@_amable
def detectar_coco(foto="principal", umbral: float = 0.3, mostrar: bool = True):
    """RT-DETRv2, entrenado con COCO: solo puede responder con una de sus 80 clases."""
    torch = _torch()
    umbral = _validar_umbral(umbral)
    ruta = _ruta_foto(foto)
    modelo, procesador = _cargar("rtdetr")
    imagen = _abrir_foto(ruta)
    inicio = time.perf_counter()
    with torch.inference_mode():
        salida = modelo(**procesador(images=imagen, return_tensors="pt"))
    res = procesador.post_process_object_detection(salida, threshold=umbral,
                                                   target_sizes=torch.tensor([[imagen.height, imagen.width]]))[0]
    segundos = time.perf_counter() - inicio
    etiquetas = [modelo.config.id2label[int(k)] for k in res["labels"]]
    d = Deteccion(ruta.name, imagen, f"RT-DETRv2 (COCO) · umbral {umbral:g} · {ruta.name}", res["boxes"].numpy(),
                  res["scores"].numpy(), etiquetas, segundos)
    conteo = {}
    for e in etiquetas:
        conteo[e] = conteo.get(e, 0) + 1
    resumen = ", ".join(f"{v} «{k}»" for k, v in sorted(conteo.items(), key=lambda t: -t[1])) or "ninguna caja"
    RESULTADOS["coco"][ruta.name] = d
    _registrar(_fila("contar cápsulas", ruta.name, "preentrenado", f"RT-DETRv2 (COCO) · umbral {umbral:g}", "local",
                     MODELOS["rtdetr"]["repo"], False, resumen, tiempo_s=round(segundos, 2)))
    if mostrar:
        figuras.cajas(d)
        p.nota(f"{len(etiquetas)} cajas: {resumen}. Tardó {_n(segundos, 2)} s en la CPU.", "neutro",
               "Lo que ve un detector entrenado con COCO")
    return d


def contar_4a(foto="principal"):
    """El pipeline del 4A con su configuración de la solución, comparado con la referencia."""
    try:
        import inspeccion as insp
    except ImportError:
        raise ErrorDeLaboratorio("Faltan las librerías del 4A (OpenCV, scikit-image o SciPy): ejecute la primera celda.") from None
    ruta = _ruta_foto(foto)
    inicio = time.perf_counter()
    r = insp.procesar(insp.cargar(str(ruta)), CONFIG_4A, ruta.name)
    segundos = time.perf_counter() - inicio
    ref = _referencia(ruta)
    comp = insp.comparar(r, ref) if ref else None
    RESULTADOS["4a"][ruta.name] = (r, comp, segundos)
    if comp:
        resumen = (f"{r.conteo} regiones: {len(comp.correctas)} con una cápsula, {len(comp.fusionadas)} que juntan dos o "
                   f"más, {len(comp.sobrantes)} sin cápsula; {len(comp.perdidas)} cápsulas perdidas")
        _registrar(_fila("contar cápsulas", ruta.name, "clasico", "pipeline del 4A (configuración de la solución)", "local",
                         "OpenCV y scikit-image", comp.exacta, resumen, tiempo_s=round(segundos, 3)))
    return r, comp, segundos


# El alargamiento (largo ÷ ancho) de la cápsula típica en el 4A: la mediana del lote de capsulas_deforme.jpg
ALARGAMIENTO_TIPICO = 2.23


@_amable
def regla_alargamiento(conjunto, tolerancia: float = 12, mostrar: bool = True):
    """La regla del 4A: se rechaza la cápsula cuyo alargamiento se aleja del típico más que la tolerancia, en %."""
    try:
        import inspeccion as insp
    except ImportError:
        raise ErrorDeLaboratorio("Faltan las librerías del 4A (OpenCV, scikit-image o SciPy): ejecute la primera celda.") from None
    if conjunto is None:
        raise ErrorDeLaboratorio("No hay imágenes cargadas: revise la celda donde se cargan.")
    config = {**CONFIG_4A, "separar": False}   # cada recorte tiene una sola cápsula
    medidas = []
    inicio = time.perf_counter()
    for img in conjunto.imagenes:
        r = insp.procesar(np.asarray(img.imagen)[:, :, ::-1].copy(), config, img.nombre)
        g = max(r.regiones, key=lambda g: g.area) if r.regiones else None
        alargamiento = g.largo / g.ancho if g else float("nan")
        desviacion = 100 * (alargamiento / ALARGAMIENTO_TIPICO - 1)
        medidas.append((img, alargamiento, desviacion, bool(g) and abs(desviacion) > tolerancia))
    segundos = (time.perf_counter() - inicio) / len(conjunto.imagenes)
    filas = []
    for k in conjunto.clases:
        de_k = [m for m in medidas if m[0].clase == k]
        filas.append({"clase real": k, "rechazadas por la regla": f"{sum(m[3] for m in de_k)} de {len(de_k)}",
                      "alargamiento (mín. – máx.)": f"{_n(min(m[1] for m in de_k), 2)} – {_n(max(m[1] for m in de_k), 2)}"})
    deformes = [m for m in medidas if m[0].clase == "deforme"]
    otras = [m for m in medidas if m[0].clase != "deforme"]
    resultado = {"detectadas": sum(m[3] for m in deformes), "deformes": len(deformes),
                 "falsas": sum(m[3] for m in otras), "otras": len(otras), "segundos": segundos, "tolerancia": tolerancia}
    RESULTADOS["regla"] = resultado
    for img, alargamiento, desviacion, rechazada in medidas:
        _registrar(_fila("rechazar cápsulas deformes", img.nombre, "clasico",
                         f"regla del alargamiento del 4A · tolerancia {tolerancia:g} %", "local", "OpenCV y scikit-image",
                         rechazada == (img.clase == "deforme"), "rechazada" if rechazada else "aceptada",
                         tiempo_s=round(segundos, 4), notas=f"alargamiento {alargamiento:.2f}; {desviacion:+.1f} % frente al típico"))
    if mostrar:
        p.mostrar_tabla(filas, titulo=f"La regla del 4A: alargamiento típico {_n(ALARGAMIENTO_TIPICO, 2)}, tolerancia ±{tolerancia:g} %")
        normales = sum(m[3] for m in otras if m[0].clase == "normal")
        p.nota(f"Rechaza {resultado['detectadas']} de las {resultado['deformes']} cápsulas deformes. También rechaza "
               f"{resultado['falsas']} de las {resultado['otras']} que no son deformes: {normales} sin defecto y "
               f"{resultado['falsas'] - normales} con otro defecto. Tarda {_n(1000 * segundos, 0)} ms por imagen.", "neutro",
               "Una medida diseñada a mano")
    return resultado


@_amable
def validar_detector(texto: str, umbral: float) -> None:
    """El detector y el pipeline del 4A en las tres fotos, frente al conteo a mano."""
    filas = []
    for clave, nombre in FOTOS_CASO.items():
        d = detectar_texto(clave, texto, umbral, mostrar=False)
        if d is None:
            return
        r, comp, seg = contar_4a(clave)
        c = d.comparacion
        filas.append({"foto": nombre, "a mano": c["cantidad"],
                      "OWLv2: cajas": d.conteo, "OWLv2: bien": f"{len(c['correctas'])} de {c['cantidad']}",
                      "pipeline 4A: regiones": r.conteo, "4A: bien": f"{len(comp.correctas)} de {comp.cantidad}",
                      "s por foto (OWLv2 / 4A)": f"{_n(d.segundos, 1)} / {_n(seg, 2)}"})
    p.mostrar_tabla(filas, titulo=f"Contar las tres fotos · OWLv2 con «{texto}» y umbral {umbral:g} · pipeline del 4A")
    exactas = sum(1 for k in FOTOS_CASO.values() if RESULTADOS["deteccion"][k].exacta)
    p.nota(f"OWLv2 deja cada cápsula en su caja en {exactas} de 3 fotos. «Bien» cuenta las cajas o regiones con "
           "exactamente una cápsula de la referencia.", "exito" if exactas == 3 else "info")


@_amable
def comparar_en_foto(foto="limite") -> None:
    """Lado a lado en una foto: las regiones del pipeline del 4A y las cajas de la última detección con texto."""
    ruta = _ruta_foto(foto)
    if ruta.name not in RESULTADOS["deteccion"] or ruta.name not in RESULTADOS["4a"]:
        raise ErrorDeLaboratorio("Primero ejecute la celda que valida el detector en las tres fotos.")
    r, comp, _ = RESULTADOS["4a"][ruta.name]
    figuras.regiones_4a(r, comp, f"Pipeline del 4A · {ruta.name}")
    figuras.cajas(RESULTADOS["deteccion"][ruta.name])


# ------------------------------------------------------------------ comparación y CSV común

def tabla_comparacion() -> None:
    """Los enfoques del laboratorio lado a lado: resultado, costo, tiempo y si las imágenes salen del computador."""
    filas = []
    conteos = [(k, RESULTADOS["4a"].get(v), RESULTADOS["deteccion"].get(v)) for k, v in FOTOS_CASO.items()]
    if all(t[1] for t in conteos):
        filas.append({"enfoque": "Pipeline clásico del 4A", "tarea": "contar (3 fotos)",
                      "resultado": " · ".join(f"{NOMBRES_FOTOS[k]}: {len(t[1].correctas)} de {t[1].cantidad} bien"
                                              for k, t, _ in conteos),
                      "US$ por 1000 imágenes": "0", "tiempo por imagen": f"{_n(1000 * np.mean([t[2] for _, t, _ in conteos]), 0)} ms",
                      "¿la imagen sale del computador?": "no"})
    if all(t[2] for t in conteos):
        d0 = conteos[0][2]
        filas.append({"enfoque": f"Detector OWLv2 ({d0.descripcion.split(' · ')[1]}, {d0.descripcion.split(' · ')[2]})",
                      "tarea": "contar (3 fotos)",
                      "resultado": " · ".join(f"{NOMBRES_FOTOS[k]}: {len(d.comparacion['correctas'])} de "
                                              f"{d.comparacion['cantidad']} bien" for k, _, d in conteos),
                      "US$ por 1000 imágenes": "0", "tiempo por imagen": f"{_n(np.mean([d.segundos for _, _, d in conteos]), 1)} s",
                      "¿la imagen sale del computador?": "no"})
    regla = RESULTADOS.get("regla")
    if regla:
        filas.append({"enfoque": f"Regla del alargamiento del 4A (±{regla['tolerancia']:g} %)",
                      "tarea": "rechazar deformes (32 cápsulas)",
                      "resultado": f"rechaza {regla['detectadas']} de {regla['deformes']} deformes y {regla['falsas']} de las "
                                   f"{regla['otras']} restantes", "US$ por 1000 imágenes": "0",
                      "tiempo por imagen": f"{_n(1000 * regla['segundos'], 0)} ms", "¿la imagen sale del computador?": "no"})
    clip = [c for c in RESULTADOS["clip"].values() if c.clases == list(CLASES_CASO)]
    for c in clip:
        filas.append({"enfoque": f"CLIP · {c.nombre}", "tarea": "clasificar (32 cápsulas)",
                      "resultado": f"{c.aciertos} de 32 ({_pct(c.exactitud)})", "US$ por 1000 imágenes": "0",
                      "tiempo por imagen": f"{_n(1000 * c.metricas['segundos_por_imagen'], 0)} ms",
                      "¿la imagen sale del computador?": "no"})
    for lado in sorted(k for k in RESULTADOS["llm"] if isinstance(k, int)):
        c = RESULTADOS["llm"][lado]
        m, n = c.metricas, len(c.imagenes)
        sale = ("no (modelo local)" if m["proveedor"] == "ollama" else
                "sí, en la corrida grabada" if m["proveedor"] == "grabado" else "sí, a la nube del proveedor")
        filas.append({"enfoque": f"LLM {m['modelo']} · {lado} px", "tarea": f"clasificar ({n} cápsulas)",
                      "resultado": f"{c.aciertos} de {n} ({_pct(c.exactitud)})",
                      "US$ por 1000 imágenes": _n(1000 * m["costo_usd"] / n, 2),
                      "tiempo por imagen": f"{_n(m['segundos'] / n, 1)} s", "¿la imagen sale del computador?": sale})
    if not filas:
        p.nota("Todavía no hay resultados: ejecute las secciones 2 a 4.", "info")
        return
    p.mostrar_tabla(filas, titulo="Los enfoques del laboratorio, lado a lado")


COLUMNAS_CSV = ["sesion", "laboratorio", "pareja", "fecha", "tarea", "instancia", "metodo", "estrategia", "proveedor",
                "modelo", "correcto", "resultado", "iteraciones", "llamadas", "tokens_entrada", "tokens_salida",
                "tokens_razonamiento", "costo_usd", "tiempo_s", "notas"]


def _fila(tarea, instancia, metodo, estrategia, proveedor, modelo, correcto, resultado, llamadas=0, tokens_entrada=0,
          tokens_salida=0, tokens_razonamiento=0, costo_usd=0, tiempo_s="", notas="") -> dict:
    return {"sesion": 4, "laboratorio": "4B", "fecha": date.today().isoformat(), "tarea": tarea, "instancia": instancia,
            "metodo": metodo, "estrategia": estrategia, "proveedor": proveedor, "modelo": modelo,
            "correcto": int(bool(correcto)), "resultado": resultado, "iteraciones": 1, "llamadas": llamadas,
            "tokens_entrada": tokens_entrada, "tokens_salida": tokens_salida, "tokens_razonamiento": tokens_razonamiento,
            "costo_usd": costo_usd, "tiempo_s": tiempo_s, "notas": notas}


def _registrar(fila: dict) -> None:
    _REGISTRO[(fila["metodo"], fila["estrategia"], fila["instancia"])] = fila


def exportar_csv(pareja: str, ruta: str = "resultados_4B.csv") -> Path | None:
    """Escribe en el CSV común del contrapunto todas las corridas de esta sesión del kernel."""
    if not _REGISTRO:
        p.nota("No hay resultados para exportar: ejecute antes las secciones 2 a 4.", "aviso")
        return None
    if not isinstance(pareja, str) or not pareja.strip() or pareja.strip() == "Nombre 1 y Nombre 2":
        p.nota("Escriba los nombres de la pareja en PAREJA para que el CSV sea suyo.", "aviso")
    destino = Path(ruta)
    with destino.open("w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=COLUMNAS_CSV)
        escritor.writeheader()
        for fila in _REGISTRO.values():
            escritor.writerow({**fila, "pareja": pareja})
    grupos = {}
    for fila in _REGISTRO.values():
        g = grupos.setdefault((fila["metodo"], fila["estrategia"]), {"filas": 0, "correcto = 1": 0, "costo": 0.0})
        g["filas"] += 1
        g["correcto = 1"] += fila["correcto"]
        g["costo"] += float(fila["costo_usd"] or 0)
    p.mostrar_tabla([{"método": m, "estrategia": e, "filas": g["filas"], "correcto = 1": g["correcto = 1"],
                      "costo (US$)": _n(g["costo"], 5)} for (m, e), g in grupos.items()],
                    titulo=f"{len(_REGISTRO)} filas guardadas en {destino}")
    return destino
