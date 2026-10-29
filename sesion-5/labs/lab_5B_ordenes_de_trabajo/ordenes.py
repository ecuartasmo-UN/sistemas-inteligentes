"""Las órdenes de trabajo del Laboratorio 5B (Sesión 5 de Sistemas Inteligentes): tres arquitecturas y un LLM.

Reúne lo que el notebook necesita para enviar cada orden de MantenIA al equipo que debe atenderla:
- las órdenes etiquetadas (o los textos propios de la pareja), separadas en entrenamiento, prueba y trampas;
- tres arquitecturas con los mismos ejemplos: una bolsa de palabras con la red del 5A, una red recurrente (LSTM)
  entrenada desde cero y un transformer preentrenado (Granite, congelado) con la misma red del 5A encima;
- el LLM del contrapunto, a través del cliente común, con una instrucción fija;
- la comparación y el registro en el CSV común del contrapunto.

Todo corre en la CPU. Los errores de configuración se muestran en español, en una caja roja, sin traza.
"""
from __future__ import annotations

import csv
import hashlib
import io
import os
import platform
import re
import time
import unicodedata
import warnings
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import numpy as np

import cliente_llm
import graficas
import presentacion as p

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")   # en Windows, el caché copia en lugar de enlazar
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
warnings.filterwarnings("ignore", message="IProgress not found")

ARCHIVO_ORDENES = Path("datos") / "ordenes.csv"
ARCHIVO_CSV = "resultados_5B.csv"
SEMILLA = 7
EQUIPOS_CASO = ("eléctrico", "mecánico", "fugas", "instrumentación")
DEFINICIONES_CASO = {
    "eléctrico": "la energía y los equipos eléctricos: motores, tableros, breakers, contactores, variadores, cables e "
                 "iluminación.",
    "mecánico": "las piezas en movimiento: rodamientos, ejes, correas, cadenas, engranajes, acoples y poleas; ruidos, "
                "vibración, desgaste y desalineación.",
    "fugas": "los escapes de líquidos, aire, vapor o gas: goteos de aceite, agua o refrigerante; empaques, sellos, "
             "mangueras y tuberías.",
    "instrumentación": "los sensores, medidores y transmisores, sus lecturas y su calibración, las señales al PLC y las "
                       "alarmas.",
}
# El transformer preentrenado, fijado en una versión exacta del repositorio de Hugging Face
MODELO = {"repo": "ibm-granite/granite-embedding-107m-multilingual", "revision": "d6cffd338414d6a1c1f5decfad5fec62eebc90d5",
          "mb": 214, "nombre": "Granite Embedding 107M multilingüe", "autor": "IBM", "licencia": "Apache-2.0"}
EXPLICABILIDAD = {
    "bolsa de palabras": "media: se ve qué palabras cuenta, pero la red las combina",
    "red recurrente (LSTM)": "baja",
    "transformer preentrenado": "baja, aunque se pueden mostrar las órdenes de entrenamiento más parecidas",
    "LLM": "explica si se le pide, pero la explicación hay que verificarla",
}
SIN_RESPUESTA = graficas.SIN_RESPUESTA


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
    """Minúsculas, sin tildes ni espacios sobrantes: «Eléctrico » → «electrico»."""
    t = unicodedata.normalize("NFD", str(texto).strip().lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def palabras(texto: str) -> list:
    """Las palabras de un texto, en minúsculas y sin tildes: así «Presión» y «presion» cuentan igual."""
    return re.findall(r"[a-z0-9ñ]+", _normal(texto))


def _n(valor, decimales: int = 0) -> str:
    """Número en formato español: espacio para los miles y coma decimal."""
    return f"{valor:,.{decimales}f}".replace(",", " ").replace(".", ",")


def _torch():
    try:
        import torch
    except ImportError:
        intel = platform.system() == "Darwin" and platform.machine() == "x86_64"
        raise ErrorDeLaboratorio(
            "No está instalada la librería torch, que entrenan las tres arquitecturas. "
            + ("En un Mac con procesador Intel no hay torch para Python 3.13: use el respaldo en Google Colab (sección 0)."
               if intel else "Ejecute la primera celda del notebook, o preparar.ipynb, y reinicie el kernel.")) from None
    return torch


# ------------------------------------------------------------------ los textos

@dataclass
class Conjunto:
    nombre: str
    clases: list
    entrenamiento: dict                 # clase → textos, en el orden del archivo
    prueba: list                        # (texto, clase)
    trampa: list = field(default_factory=list)
    propio: bool = False
    controles: set = field(default_factory=set)     # órdenes del conjunto trampa que no tienen trampa, para comparar

    @property
    def huella(self) -> str:
        texto = repr((self.clases, self.entrenamiento, self.prueba, self.trampa))
        return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:10]

    @property
    def palabra_clase(self) -> str:
        return "clase" if self.propio else "equipo"

    def ejemplos(self, n: int) -> tuple:
        """Los n primeros textos de entrenamiento de cada clase, con su clase."""
        textos, etiquetas = [], []
        for k in self.clases:
            for t in self.entrenamiento[k][:n]:
                textos.append(t)
                etiquetas.append(k)
        return textos, etiquetas

    def maximo(self) -> int:
        return min(len(v) for v in self.entrenamiento.values())


def _leer_csv(ruta: Path) -> list:
    """Lee un CSV de Excel o de otro programa: separado por comas o por punto y coma, en UTF-8 o en la codificación de Windows."""
    datos = ruta.read_bytes()
    for codificacion in ("utf-8-sig", "cp1252"):
        try:
            texto = datos.decode(codificacion)
            break
        except UnicodeDecodeError:
            continue
    primera = texto.splitlines()[0] if texto.strip() else ""
    separador = ";" if primera.count(";") > primera.count(",") else ","
    filas = list(csv.DictReader(io.StringIO(texto), delimiter=separador))
    return [{(k or "").strip().lower(): (v or "").strip() for k, v in f.items()} for f in filas]


@_amable
def cargar_ordenes(ruta=ARCHIVO_ORDENES, mostrar: bool = True) -> Conjunto | None:
    """Lee las órdenes de MantenIA y muestra algunas de cada equipo."""
    ruta = Path(ruta)
    if not ruta.exists():
        raise ErrorDeLaboratorio(f"No encuentro {ruta}. Abra el notebook desde la carpeta del laboratorio, donde está la "
                                 "carpeta datos/, y reinicie el kernel.")
    filas = _leer_csv(ruta)
    c = Conjunto("órdenes de MantenIA", list(EQUIPOS_CASO), {k: [] for k in EQUIPOS_CASO}, [], [])
    for f in filas:
        if f["equipo"] not in EQUIPOS_CASO:
            raise ErrorDeLaboratorio(f"La orden «{f['texto']}» tiene un equipo desconocido: «{f['equipo']}».")
        if f["conjunto"] == "entrenamiento":
            c.entrenamiento[f["equipo"]].append(f["texto"])
        elif f["conjunto"] == "prueba":
            c.prueba.append((f["texto"], f["equipo"]))
        elif f["conjunto"] in ("trampa", "control"):
            c.trampa.append((f["texto"], f["equipo"]))
            if f["conjunto"] == "control":
                c.controles.add(f["texto"])
    if mostrar:
        graficas.muestra(c)
    return c


@_amable
def cargar_textos_propios(ruta, mostrar: bool = True) -> Conjunto | None:
    """Lee un CSV propio con las columnas texto y clase (y, si quiere, conjunto) y lo separa en entrenamiento y prueba."""
    ruta = Path(ruta)
    if not ruta.exists():
        carpeta = Path("mis_textos")
        if (carpeta / ruta.name).exists() and ruta.parent != carpeta:
            raise ErrorDeLaboratorio(f"No encontré {ruta}, pero sí {carpeta / ruta.name}: escriba la ruta completa, "
                                     f"\"{(carpeta / ruta.name).as_posix()}\".")
        hay = sorted(f.name for f in carpeta.glob("*.csv")) if carpeta.exists() else []
        p.nota(f"No encontré {ruta}. " + (f"En mis_textos/ hay: {', '.join(hay)}. " if hay else "")
               + "Si todavía no tiene sus textos, siga los pasos de mis_textos/LEEME.md y ejecute de nuevo.",
               "info", "Sin textos propios")
        return None
    try:
        filas = _leer_csv(ruta)
    except (csv.Error, IndexError) as e:
        raise ErrorDeLaboratorio(f"No pude leer {ruta} como CSV ({e}). Guárdelo desde Excel como «CSV UTF-8».") from None
    if not filas or "texto" not in filas[0] or "clase" not in filas[0]:
        columnas = ", ".join(f"«{k}»" for k in (filas[0] if filas else {})) or "ninguna"
        raise ErrorDeLaboratorio(f"El archivo {ruta} debe tener las columnas «texto» y «clase» en la primera fila "
                                 f"(encontré: {columnas}).")
    filas = [f for f in filas if f["texto"] and f["clase"]]
    clases = list(dict.fromkeys(f["clase"] for f in filas))
    if not 2 <= len(clases) <= 6:
        raise ErrorDeLaboratorio(f"Use de 2 a 6 clases; el archivo tiene {len(clases)}: {', '.join(clases)}.")
    por_clase = {k: [f for f in filas if f["clase"] == k] for k in clases}
    pocas = [f"{k} ({len(v)})" for k, v in por_clase.items() if len(v) < 4]
    if pocas:
        raise ErrorDeLaboratorio("Cada clase necesita al menos 4 textos (mejor 8 o más). Tienen muy pocos: "
                                 + ", ".join(pocas) + ".")
    c = Conjunto(f"mis textos ({ruta.name})", clases, {k: [] for k in clases}, [], [], propio=True)
    con_columna = "conjunto" in filas[0] and any(f["conjunto"] for f in filas)
    for k, grupo in por_clase.items():
        if con_columna:
            c.entrenamiento[k] = [f["texto"] for f in grupo if _normal(f["conjunto"]) != "prueba"]
            c.prueba += [(f["texto"], k) for f in grupo if _normal(f["conjunto"]) == "prueba"]
        else:
            # Sin columna «conjunto»: el último tercio de cada clase (al menos 2 textos) queda para la prueba
            n_prueba = max(2, round(len(grupo) / 3))
            c.entrenamiento[k] = [f["texto"] for f in grupo[:-n_prueba]]
            c.prueba += [(f["texto"], k) for f in grupo[-n_prueba:]]
    if not c.prueba:
        raise ErrorDeLaboratorio("No quedó ningún texto de prueba: marque algunos con «prueba» en la columna conjunto.")
    if mostrar:
        graficas.muestra(c)
    return c


# ------------------------------------------------------------------ las tres arquitecturas

def red_del_5a(entradas: int, salidas: int):
    """La red del Laboratorio 5A: dos capas ocultas de 64 neuronas con ReLU y dropout de 0.3, ahora con una salida por clase."""
    torch = _torch()
    from torch import nn
    torch.manual_seed(SEMILLA)
    return nn.Sequential(nn.Linear(entradas, 64), nn.ReLU(), nn.Dropout(0.3),
                         nn.Linear(64, 64), nn.ReLU(), nn.Dropout(0.3),
                         nn.Linear(64, salidas))


def _entrenar_red(red, x, y, epocas: int = 200, tasa: float = 0.001):
    """Entrena con todos los ejemplos en cada paso (son pocos) y Adam, como en el 5A."""
    torch = _torch()
    from torch import nn
    optimizador = torch.optim.Adam(red.parameters(), lr=tasa)
    perdida = nn.CrossEntropyLoss()
    for _ in range(epocas):
        red.train()
        optimizador.zero_grad()
        perdida(red(x), y).backward()
        optimizador.step()
    red.eval()
    return red


class BolsaDePalabras:
    nombre, corto = "bolsa de palabras", "bolsa"
    modelo = "conteo de palabras + red del 5A"

    def ajustar(self, textos, etiquetas):
        torch = _torch()
        self.vocabulario = {w: i for i, w in enumerate(sorted({w for t in textos for w in palabras(t)}))}
        self.red = _entrenar_red(red_del_5a(len(self.vocabulario), int(max(etiquetas)) + 1), self.vectores(textos),
                                 torch.tensor(etiquetas))
        return self

    def vectores(self, textos):
        torch = _torch()
        v = torch.zeros(len(textos), len(self.vocabulario))
        for i, t in enumerate(textos):
            for w in palabras(t):
                if w in self.vocabulario:           # las palabras que no vio en los ejemplos no cuentan
                    v[i, self.vocabulario[w]] += 1
        return v

    def predecir(self, textos):
        torch = _torch()
        with torch.no_grad():
            return self.red(self.vectores(textos)).argmax(1).tolist()


class RedRecurrente:
    nombre, corto = "red recurrente (LSTM)", "LSTM"
    modelo = "LSTM desde cero"

    def ajustar(self, textos, etiquetas, epocas: int = 80, dimension: int = 32, oculta: int = 32):
        torch = _torch()
        from torch import nn
        self.vocabulario = {"<relleno>": 0, "<desconocida>": 1}
        for t in textos:
            for w in palabras(t):
                self.vocabulario.setdefault(w, len(self.vocabulario))
        torch.manual_seed(SEMILLA)
        self.capas = nn.ModuleDict({"vectores": nn.Embedding(len(self.vocabulario), dimension, padding_idx=0),
                                    "lstm": nn.LSTM(dimension, oculta, batch_first=True),
                                    "salida": nn.Linear(oculta, int(max(etiquetas)) + 1)})
        x, largos = self._indices(textos)
        optimizador = torch.optim.Adam(self.capas.parameters(), lr=0.01)
        perdida = nn.CrossEntropyLoss()
        y = torch.tensor(etiquetas)
        for _ in range(epocas):
            self.capas.train()
            optimizador.zero_grad()
            perdida(self._adelante(x, largos), y).backward()
            optimizador.step()
        self.capas.eval()
        return self

    def _indices(self, textos):
        torch = _torch()
        ids = [[self.vocabulario.get(w, 1) for w in palabras(t)] or [1] for t in textos]
        x = torch.zeros(len(ids), max(len(i) for i in ids), dtype=torch.long)
        for k, i in enumerate(ids):
            x[k, :len(i)] = torch.tensor(i)
        return x, torch.tensor([len(i) for i in ids])

    def _adelante(self, x, largos):
        from torch import nn
        e = self.capas["vectores"](x)
        empacado = nn.utils.rnn.pack_padded_sequence(e, largos, batch_first=True, enforce_sorted=False)
        _, (h, _) = self.capas["lstm"](empacado)       # la memoria después de leer la última palabra
        return self.capas["salida"](h[-1])

    def predecir(self, textos):
        torch = _torch()
        with torch.no_grad():
            x, largos = self._indices(textos)
            return self._adelante(x, largos).argmax(1).tolist()


_GRANITE: dict = {}             # el tokenizador, el modelo y los vectores ya calculados


def descargado() -> bool:
    """True si Granite ya está en el caché de Hugging Face de este computador."""
    try:
        from huggingface_hub import try_to_load_from_cache
    except ImportError:
        return False
    ruta = try_to_load_from_cache(MODELO["repo"], "model.safetensors", revision=MODELO["revision"])
    return isinstance(ruta, str)


def _granite(silencioso: bool = False):
    if "modelo" in _GRANITE:
        return _GRANITE["tokenizador"], _GRANITE["modelo"]
    torch = _torch()
    try:
        import huggingface_hub
        import transformers
        from transformers import AutoModel, AutoTokenizer
    except ImportError:
        raise ErrorDeLaboratorio("No está instalada la librería transformers. Ejecute la primera celda del notebook, o "
                                 "preparar.ipynb, y reinicie el kernel.") from None
    transformers.logging.set_verbosity_error()
    transformers.utils.logging.disable_progress_bar()
    huggingface_hub.utils.logging.set_verbosity_error()
    if not descargado() and not silencioso:
        p.nota(f"Granite no está descargado en este computador: se descarga ahora ({MODELO['mb']} MB). En la red del salón "
               "puede tardar; la próxima vez quedará en el caché.", "aviso")
    inicio = time.perf_counter()
    try:
        tokenizador = AutoTokenizer.from_pretrained(MODELO["repo"], revision=MODELO["revision"])
        modelo = AutoModel.from_pretrained(MODELO["repo"], revision=MODELO["revision"], dtype=torch.float32).eval()
    except OSError as e:
        raise ErrorDeLaboratorio(f"No pude cargar Granite ({str(e)[:160]}). Si no está descargado, conéctese a internet y "
                                 "ejecute preparar.ipynb.") from None
    _GRANITE.update(tokenizador=tokenizador, modelo=modelo, vectores={}, segundos_carga=time.perf_counter() - inicio)
    return tokenizador, modelo


def vectores_granite(textos):
    """El vector de 384 números de cada texto: el del primer token (CLS), normalizado, como indica la ficha del modelo."""
    torch = _torch()
    tokenizador, modelo = _granite()
    cache = _GRANITE["vectores"]
    faltan = [t for t in dict.fromkeys(textos) if t not in cache]
    with torch.inference_mode():
        for i in range(0, len(faltan), 32):
            lote = faltan[i:i + 32]
            entrada = tokenizador(lote, padding=True, truncation=True, max_length=128, return_tensors="pt")
            v = torch.nn.functional.normalize(modelo(**entrada).last_hidden_state[:, 0], dim=-1)
            for t, fila in zip(lote, v):
                cache[t] = fila.clone()
    return torch.stack([cache[t] for t in textos])


class TransformerPreentrenado:
    nombre, corto = "transformer preentrenado", "transformer"
    modelo = "granite-embedding-107m-multilingual + red del 5A"

    def ajustar(self, textos, etiquetas):
        torch = _torch()
        self.red = _entrenar_red(red_del_5a(384, int(max(etiquetas)) + 1), vectores_granite(textos), torch.tensor(etiquetas))
        return self

    def predecir(self, textos):
        torch = _torch()
        with torch.no_grad():
            return self.red(vectores_granite(textos)).argmax(1).tolist()


ARQUITECTURAS = {"bolsa": BolsaDePalabras, "lstm": RedRecurrente, "transformer": TransformerPreentrenado}


@_amable
def comprobar_modelo() -> bool:
    """Muestra si Granite está descargado y si las librerías funcionan."""
    p.mostrar_tabla([{"modelo": f"{MODELO['nombre']} ({MODELO['autor']})", "para qué": "convertir cada orden en un vector",
                      "tamaño": f"{MODELO['mb']} MB", "licencia": MODELO["licencia"],
                      "descargado": "sí" if descargado() else "no"}], titulo="El transformer que corre en este computador")
    torch = _torch()
    try:
        import transformers
    except ImportError:
        raise ErrorDeLaboratorio("No está instalada la librería transformers. Ejecute la primera celda y reinicie el "
                                 "kernel.") from None
    version = f"torch {torch.__version__} · transformers {transformers.__version__}"
    if not descargado():
        p.nota(f"{version}. Granite no está descargado: lo ideal es ejecutar preparar.ipynb antes de la clase. Si no "
               "alcanzó, se descargará la primera vez que se use.", "aviso")
        return False
    p.nota(f"{version}. Granite está descargado: no necesita internet.", "exito")
    return True


def descargar_modelo() -> bool:
    """Para preparar.ipynb: descarga Granite y lo prueba con tres órdenes."""
    print(f"{MODELO['nombre']} ({MODELO['mb']} MB): {'ya estaba descargado' if descargado() else 'descargando…'}")
    inicio = time.perf_counter()
    try:
        _granite(silencioso=True)
        v = vectores_granite(["Hay fuga de aceite en la bomba 3", "Escape de lubricante en la bomba 3",
                              "El rodamiento de la bomba 3 hace ruido"])
    except ErrorDeLaboratorio as e:
        p.nota(str(e), "error", "No se pudo preparar Granite")
        return False
    p.nota(f"Granite listo en {_n(time.perf_counter() - inicio, 0)} s. Similitud entre «Hay fuga de aceite» y «Escape de "
           f"lubricante»: {_n(float(v[0] @ v[1]), 2)}; con «El rodamiento hace ruido»: {_n(float(v[0] @ v[2]), 2)}.",
           "exito", "✓ Preparación completa")
    return True


# ------------------------------------------------------------------ clasificar y evaluar

@dataclass
class Clasificacion:
    metodo: str                     # el nombre de la arquitectura, o «LLM»
    estrategia: str                 # «10 ejemplos por equipo» o «instrucción sin ejemplos»
    clases: list
    textos: list
    reales: list
    asignadas: list                 # None = sin respuesta válida
    grupos: list                    # «prueba», «trampa» o «propia»
    ejemplos: int = 0
    proveedor: str = "local"
    modelo: str = ""
    segundos_entrenar: float = 0.0
    segundos_clasificar: float = 0.0
    tokens_entrada: list = field(default_factory=list)
    tokens_salida: list = field(default_factory=list)
    costos: list = field(default_factory=list)
    tiempos: list = field(default_factory=list)
    respuestas: list = field(default_factory=list)

    def aciertos(self, grupo: str = "prueba") -> int:
        return sum(1 for r, a, g in zip(self.reales, self.asignadas, self.grupos) if g == grupo and r == a)

    def total(self, grupo: str = "prueba") -> int:
        return sum(1 for g in self.grupos if g == grupo)

    def del_grupo(self, grupo: str = "prueba"):
        """La misma clasificación, solo con los textos del grupo, para la matriz de confusión."""
        indices = [i for i, g in enumerate(self.grupos) if g == grupo]
        return Clasificacion(self.metodo, self.estrategia, self.clases, [self.textos[i] for i in indices],
                             [self.reales[i] for i in indices], [self.asignadas[i] for i in indices], [grupo] * len(indices),
                             self.ejemplos)

    @property
    def titulo(self) -> str:
        return f"{self.metodo} · {self.estrategia}"


_HECHAS: dict = {}          # cada (conjunto, arquitectura, ejemplos) ya entrenado en esta sesión del kernel
_REGISTRO: dict = {}        # las filas del CSV común: (método, estrategia, instancia) → fila


def _validar_cantidad(n, conjunto: Conjunto, nombre: str = "la cantidad de ejemplos") -> int:
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise ErrorDeLaboratorio(f"Cada cantidad de ejemplos es un número entero mayor que 0, sin comillas (encontré {n!r}).")
    return n


def _a_clasificar(conjunto: Conjunto, extras=()) -> tuple:
    textos = [t for t, _ in conjunto.prueba] + [t for t, _ in conjunto.trampa] + [t for t, _ in extras]
    reales = [k for _, k in conjunto.prueba] + [k for _, k in conjunto.trampa] + [k for _, k in extras]
    grupos = ["prueba"] * len(conjunto.prueba) + ["trampa"] * len(conjunto.trampa) + ["propia"] * len(extras)
    return textos, reales, grupos


def _entrenar_y_clasificar(conjunto: Conjunto, clave: str, n: int) -> Clasificacion:
    """Entrena una arquitectura con los n primeros ejemplos de cada clase y clasifica la prueba y las trampas."""
    llave = (conjunto.huella, clave, n)
    if llave in _HECHAS:
        return _HECHAS[llave]
    Arquitectura = ARQUITECTURAS[clave]
    textos_e, clases_e = conjunto.ejemplos(n)
    indice = {k: i for i, k in enumerate(conjunto.clases)}
    inicio = time.perf_counter()
    modelo = Arquitectura().ajustar(textos_e, [indice[k] for k in clases_e])
    entrenar = time.perf_counter() - inicio
    textos, reales, grupos = _a_clasificar(conjunto)
    inicio = time.perf_counter()
    asignadas = [conjunto.clases[i] for i in modelo.predecir(textos)]
    clasificar = time.perf_counter() - inicio
    usados = min(n, conjunto.maximo())
    c = Clasificacion(Arquitectura.nombre, f"{usados} ejemplos por {conjunto.palabra_clase}", conjunto.clases, textos,
                      reales, asignadas, grupos, usados, "local", Arquitectura.modelo, entrenar, clasificar)
    c.modelo_entrenado = modelo
    _HECHAS[llave] = c
    for i, t in enumerate(textos):
        _registrar(conjunto, c, i)
    return c


def _registrar(conjunto: Conjunto, c: Clasificacion, i: int) -> None:
    llm = c.metodo == "LLM"
    fila = {"sesion": 5, "laboratorio": "5B", "fecha": date.today().isoformat(),
            "tarea": "clasificar textos propios" if conjunto.propio else "asignar órdenes de trabajo",
            "instancia": c.textos[i], "metodo": c.metodo if not llm else "LLM", "estrategia": c.estrategia,
            "proveedor": c.proveedor, "modelo": c.modelo, "correcto": int(c.asignadas[i] == c.reales[i]),
            "resultado": c.asignadas[i] or SIN_RESPUESTA, "iteraciones": 1, "llamadas": 1 if llm else 0,
            "tokens_entrada": c.tokens_entrada[i] if llm else 0, "tokens_salida": c.tokens_salida[i] if llm else 0,
            "tokens_razonamiento": 0, "costo_usd": round(c.costos[i], 7) if llm and c.costos[i] is not None else 0,
            "tiempo_s": round(c.tiempos[i], 3) if llm else round((c.segundos_entrenar + c.segundos_clasificar) / len(c.textos), 4),
            "notas": f"{c.grupos[i]} · real: {c.reales[i]} · {conjunto.nombre}"}
    _REGISTRO[(fila["metodo"], fila["estrategia"], conjunto.huella, c.textos[i])] = fila


@_amable
def clasificar(conjunto: Conjunto, arquitectura: str, ejemplos: int = 10, mostrar: bool = True) -> Clasificacion | None:
    """Entrena una arquitectura con los mismos ejemplos de cada clase y muestra sus aciertos en las órdenes de prueba."""
    if conjunto is None:
        raise ErrorDeLaboratorio("Primero ejecute la celda que carga las órdenes (sección 1).")
    ejemplos = _validar_cantidad(ejemplos, conjunto)
    c = _entrenar_y_clasificar(conjunto, arquitectura, ejemplos)
    if mostrar:
        prueba = c.del_grupo("prueba")
        graficas.matriz(prueba, f"Matriz de confusión · {c.titulo}")
        clasificar_s = "menos de 0,01 s" if c.segundos_clasificar < 0.01 else f"{_n(c.segundos_clasificar, 2)} s"
        detalle = (f" ({c.total('prueba')} de prueba y {c.total('trampa')} trampas y controles)" if c.total("trampa")
                   else "")
        p.nota(f"Entrenó con {c.ejemplos * len(conjunto.clases)} ejemplos en {_n(c.segundos_entrenar, 1)} s y clasificó "
               f"{len(c.textos)} {'textos' if conjunto.propio else 'órdenes'}{detalle} en {clasificar_s}, en la CPU.", "info")
        conocidas = None
        if arquitectura != "transformer":       # las palabras que esta arquitectura vio en los ejemplos
            conocidas = {w for t in conjunto.ejemplos(c.ejemplos)[0] for w in palabras(t)}
        graficas.errores(prueba, conocidas=conocidas, normalizar=_normal)
    return c


@_amable
def mas_parecidas(conjunto: Conjunto, texto: str, ejemplos: int = 10, cuantas: int = 3) -> None:
    """Las órdenes de entrenamiento más parecidas a un texto según el transformer, y las palabras que comparten."""
    textos_e, clases_e = conjunto.ejemplos(ejemplos)
    v = vectores_granite([texto] + textos_e)
    similitud = (v[1:] @ v[0]).tolist()
    orden = sorted(range(len(textos_e)), key=lambda i: -similitud[i])[:cuantas]
    propias = set(palabras(texto))
    p.mostrar_tabla([{"orden de entrenamiento": textos_e[i], conjunto.palabra_clase: clases_e[i],
                      "similitud según el transformer": _n(similitud[i], 2),
                      "palabras en común": ", ".join(sorted(propias & set(palabras(textos_e[i])))) or "ninguna"}
                     for i in orden], titulo=f"Las {cuantas} órdenes de entrenamiento más parecidas a «{texto}»")


@_amable
def comparar_cantidades(conjunto: Conjunto, cantidades, llm_resultado: Clasificacion | None = None) -> list | None:
    """Entrena las tres arquitecturas con cada cantidad de ejemplos por clase y compara sus aciertos en la prueba."""
    if conjunto is None:
        raise ErrorDeLaboratorio("No hay textos que clasificar: ejecute antes la celda que los carga.")
    if not isinstance(cantidades, (list, tuple)) or not cantidades:
        raise ErrorDeLaboratorio("La lista de cantidades va entre corchetes, por ejemplo [3, 10, 30].")
    if len(cantidades) > 6:
        raise ErrorDeLaboratorio("Compare como máximo 6 cantidades a la vez.")
    cantidades = sorted({_validar_cantidad(n, conjunto) for n in cantidades})
    maximo = conjunto.maximo()
    if any(n > maximo for n in cantidades):
        p.nota(f"La clase con menos textos de entrenamiento tiene {maximo}: las cantidades mayores usan los que haya.",
               "aviso")
        cantidades = sorted({min(n, maximo) for n in cantidades})
    resultados = [_entrenar_y_clasificar(conjunto, clave, n) for n in cantidades for clave in ARQUITECTURAS]
    graficas.curva_cantidades(resultados, conjunto, llm_resultado)
    filas = []
    for n in cantidades:
        fila = {f"ejemplos por {conjunto.palabra_clase}": n}
        for r in resultados:
            if r.ejemplos == n:
                fila[r.metodo] = f"{r.aciertos()} de {r.total()}"
        filas.append(fila)
    p.mostrar_tabla(filas, titulo=f"Aciertos en {'los' if conjunto.propio else 'las'} {len(conjunto.prueba)} "
                                  f"{'textos' if conjunto.propio else 'órdenes'} de prueba")
    if len(conjunto.prueba) < 30:
        p.nota(f"Con {len(conjunto.prueba)} textos de prueba, cada uno vale {round(100 / len(conjunto.prueba))} puntos "
               "porcentuales: "
               "una diferencia de uno o dos textos entre arquitecturas o cantidades no es concluyente.", "info")
    if len(cantidades) < 3:
        p.nota("Agregue más cantidades a la lista, por ejemplo [3, 10, 30], y ejecute de nuevo: las que ya corrieron no se "
               "repiten.", "aviso", "Falta una cantidad")
    return resultados


def _validar_ordenes(mis_ordenes, conjunto: Conjunto) -> list:
    if mis_ordenes is None:
        return []
    if not isinstance(mis_ordenes, dict):
        raise ErrorDeLaboratorio("Las órdenes o los textos van en un diccionario entre llaves: "
                                 "{\"el texto\": \"su clase\", ...}.")
    por_nombre = {_normal(k): k for k in conjunto.clases}
    salida = []
    for texto, clase in mis_ordenes.items():
        if not isinstance(texto, str) or not texto.strip():
            raise ErrorDeLaboratorio("Cada orden o texto va entre comillas.")
        if not isinstance(clase, str) or _normal(clase) not in por_nombre:
            articulo, uno = ("La", "una") if conjunto.propio else ("El", "uno")
            raise ErrorDeLaboratorio(f"{articulo} {conjunto.palabra_clase} de «{texto}» es «{clase}», que no existe. Use {uno} "
                                     "de: " + ", ".join(conjunto.clases) + ".")
        salida.append((texto.strip(), por_nombre[_normal(clase)]))
    return salida


@_amable
def poner_a_prueba(conjunto: Conjunto, mis_ordenes=None, ejemplos: int = 10) -> list | None:
    """Las tres arquitecturas, entrenadas con los mismos ejemplos, frente a las órdenes trampa y las de la pareja."""
    if conjunto is None:
        raise ErrorDeLaboratorio("Primero ejecute la celda que carga las órdenes (sección 1).")
    ejemplos = min(_validar_cantidad(ejemplos, conjunto), conjunto.maximo())
    propias = _validar_ordenes(mis_ordenes, conjunto)
    filas = [(t, k, "control" if t in conjunto.controles else "trampa") for t, k in conjunto.trampa] + \
        [(t, k, "suyo" if conjunto.propio else "suya") for t, k in propias]
    modelos = {clave: _entrenar_y_clasificar(conjunto, clave, ejemplos) for clave in ARQUITECTURAS}
    respuestas = {clave: [conjunto.clases[i] for i in c.modelo_entrenado.predecir([t for t, _, _ in filas])]
                  for clave, c in modelos.items()} if filas else {}
    titulo = "Sus textos difíciles" if conjunto.propio else "Las órdenes trampa y las suyas"
    graficas.tabla_pruebas(filas, respuestas, [ARQUITECTURAS[k].nombre for k in ARQUITECTURAS],
                           f"{titulo} · {ejemplos} ejemplos por {conjunto.palabra_clase}",
                           columna="texto" if conjunto.propio else "orden")
    if not propias:
        p.nota("Escriba dos o tres textos suyos, con la clase que les corresponde, y ejecute de nuevo." if conjunto.propio
               else "Escriba en MIS_ORDENES dos o tres órdenes suyas, con el equipo que debería atenderlas, y ejecute de "
                    "nuevo.", "aviso", "Faltan sus textos" if conjunto.propio else "Faltan sus órdenes")
    return respuestas


@_amable
def similitudes(frases) -> None:
    """La similitud entre la primera frase y las demás, según el transformer y según la bolsa de palabras."""
    if not isinstance(frases, (list, tuple)) or len(frases) < 2:
        raise ErrorDeLaboratorio("FRASES es una lista de al menos dos frases entre comillas.")
    v = vectores_granite(list(frases))
    base = set(palabras(frases[0]))

    def coseno_bolsa(a, b):
        ca, cb = [palabras(x) for x in (a, b)]
        voc = sorted(set(ca) | set(cb))
        x = np.array([ca.count(w) for w in voc], float)
        y = np.array([cb.count(w) for w in voc], float)
        return float(x @ y / (np.linalg.norm(x) * np.linalg.norm(y) or 1))
    p.mostrar_tabla([{"frente a": f, "según el transformer": _n(float(v[0] @ v[i + 1]), 2),
                      "según la bolsa de palabras": _n(coseno_bolsa(frases[0], f), 2),
                      "palabras que no comparten": ", ".join(sorted(base ^ set(palabras(f)))) or "ninguna"}
                     for i, f in enumerate(frases[1:])],
                    titulo=f"Similitud con «{frases[0]}» (1 = idénticas)")


# ------------------------------------------------------------------ el LLM

def instruccion(conjunto: Conjunto, definiciones: dict | None = None) -> str:
    """La instrucción de sistema: quién responde, las clases con su definición y el formato de la respuesta."""
    if not conjunto.propio:
        lineas = "\n".join(f"- {k}: {DEFINICIONES_CASO[k]}" for k in conjunto.clases)
        return ("Usted despacha las órdenes de trabajo de MantenIA, una empresa de mantenimiento industrial. Cada orden "
                f"va a uno de estos cuatro equipos:\n{lineas}\nResponda solo con el nombre del equipo, sin explicación.")
    definiciones = definiciones or {}
    lineas = "\n".join(f"- {k}" + (f": {definiciones[k]}" if definiciones.get(k) else "") for k in conjunto.clases)
    return ("Usted clasifica textos cortos de una organización. Cada texto va a una de estas clases:\n"
            f"{lineas}\nResponda solo con el nombre de la clase, sin explicación.")


def mostrar_instruccion(conjunto: Conjunto) -> None:
    """Muestra la instrucción que recibe el LLM con cada orden."""
    p.mostrar_conversacion([{"role": "system", "content": instruccion(conjunto)},
                            {"role": "user", "content": f"Orden: {conjunto.prueba[0][0]}"}],
                           "La instrucción y una orden, como las recibe el LLM", abierta=True,
                           etiquetas={"user": "Mensaje con la orden"})


def _leer_respuesta(texto: str, clases) -> str | None:
    """La clase si la respuesta es exactamente una de ellas (sin contar mayúsculas, tildes ni el punto final); si no, None."""
    limpio = _normal(texto).strip(" .:;\"'*`\n")
    return {_normal(k): k for k in clases}.get(limpio)


_LLM_HECHAS: dict = {}


@_amable
def clasificar_llm(llm, conjunto: Conjunto, experimento: str = "clase", definiciones: dict | None = None,
                   extras=(), mostrar: bool = True) -> Clasificacion | None:
    """Envía cada orden de prueba y cada trampa al LLM, con la misma instrucción, y mide aciertos, tokens, costo y tiempo."""
    if llm is None:
        raise ErrorDeLaboratorio("El LLM no está configurado: ejecute la celda de la sección 0.2.")
    if conjunto is None:
        raise ErrorDeLaboratorio("Primero ejecute la celda que carga los textos.")
    if llm.proveedor == "grabado" and conjunto.propio:
        p.nota("Con respuestas grabadas no hay respuestas para sus textos. Para clasificarlos con un LLM, configure una "
               "clave de API o Ollama en la sección 0.2, o use el chat del LLM, como dice el enunciado del TI-2.", "aviso")
        return None
    sistema = instruccion(conjunto, definiciones)
    textos, reales, grupos = _a_clasificar(conjunto, extras)
    llave = (conjunto.huella, experimento, sistema, tuple(textos), llm.proveedor, llm.modelo)
    if llave in _LLM_HECHAS:
        c = _LLM_HECHAS[llave]
    else:
        c = Clasificacion("LLM", "instrucción sin ejemplos" + ("" if experimento == "clase" else f" · {experimento}"),
                          conjunto.clases, [], [], [], [], 0, llm.proveedor, llm.modelo)
        prefijo = "Texto" if conjunto.propio else "Orden"
        faltaron = 0
        if llm.proveedor != "grabado":
            print(f"Enviando {len(textos)} {'textos' if conjunto.propio else 'órdenes'} al LLM…")
        for t, k, g in zip(textos, reales, grupos):
            r = llm.completar([{"role": "user", "content": f"{prefijo}: {t}"}], sistema=sistema,
                              etiqueta=f"5B · {experimento} · {t}", max_tokens_respuesta=20)
            if not r.disponible:
                faltaron += 1
                continue
            c.textos.append(t), c.reales.append(k), c.grupos.append(g), c.respuestas.append(r.texto)
            c.asignadas.append(_leer_respuesta(r.texto, conjunto.clases))
            c.tokens_entrada.append(r.tokens_entrada), c.tokens_salida.append(r.tokens_salida)
            c.costos.append(r.costo_usd), c.tiempos.append(r.segundos)
        if faltaron:
            p.nota(f"{faltaron} textos no tienen respuesta grabada y quedaron fuera. Para clasificarlos, configure una clave "
                   "de API o un modelo local.", "aviso")
        if not c.textos:
            return None
        c.segundos_clasificar = sum(c.tiempos)
        _LLM_HECHAS[llave] = c
        for i in range(len(c.textos)):
            _registrar(conjunto, c, i)
    if mostrar:
        graficas.matriz(c.del_grupo("prueba"), f"Matriz de confusión · LLM · {llm.modelo}")
        _resumen_llm(c, conjunto)
        graficas.errores(c.del_grupo("prueba"), respuestas=dict(zip(c.textos, c.respuestas)))
    return c


def _costo_por_mil(c: Clasificacion):
    costos = [x for x in c.costos if x is not None]
    return 1000 * sum(costos) / len(costos) if costos and len(costos) == len(c.costos) else None


def _resumen_llm(c: Clasificacion, conjunto: Conjunto) -> None:
    n = len(c.textos)
    invalidas = sum(1 for a in c.asignadas if a is None)
    por_mil = _costo_por_mil(c)
    costo = ("sin costo monetario (modelo local)" if c.proveedor == "ollama" else
             f"US${_n(sum(c.costos), 4)} en total, unos US${_n(por_mil, 3)} por cada 1000 órdenes" if por_mil is not None
             else "precio no registrado")
    trampas = f" y {c.aciertos('trampa')} de {c.total('trampa')} trampas y controles" if c.total("trampa") else ""
    p.nota(f"{c.aciertos()} de {c.total()} de prueba{trampas}; {invalidas} sin respuesta válida. "
           f"{n} llamadas: {_n(sum(c.tokens_entrada) / n, 0)} tokens de entrada y {_n(sum(c.tokens_salida) / n, 0)} de salida "
           f"por orden; {costo}; {_n(sum(c.tiempos) / n, 2)} s por orden.",
           "info", f"El LLM · {c.modelo}")


@_amable
def repetir_llm(llm, conjunto: Conjunto, repeticiones: int = 2) -> list | None:
    """Envía otra vez las mismas órdenes, con la misma instrucción, y muestra las que cambiaron de equipo."""
    if isinstance(repeticiones, bool) or not isinstance(repeticiones, int) or not 1 <= repeticiones <= 5:
        raise ErrorDeLaboratorio(f"REPETICIONES es un número entero de 1 a 5 (escribió {repeticiones!r}).")
    corridas = [clasificar_llm(llm, conjunto, "clase", mostrar=False)]
    corridas += [clasificar_llm(llm, conjunto, f"repetición {i}", mostrar=False) for i in range(1, repeticiones + 1)]
    corridas = [c for c in corridas if c is not None]
    if len(corridas) < 2:
        return None
    p.mostrar_tabla([{"corrida": c.estrategia, "aciertos en prueba": f"{c.aciertos()} de {c.total()}",
                      "trampas y controles": f"{c.aciertos('trampa')} de {c.total('trampa')}",
                      "sin respuesta válida": sum(1 for a in c.asignadas if a is None)} for c in corridas],
                    titulo="El LLM, con las mismas órdenes y la misma instrucción")
    respuestas = {}
    for c in corridas:
        for t, a in zip(c.textos, c.asignadas):
            respuestas.setdefault(t, []).append(a or SIN_RESPUESTA)
    cambiaron = [{"orden": t, "respuestas": " · ".join(r)} for t, r in respuestas.items() if len(set(r)) > 1]
    if cambiaron:
        p.mostrar_tabla(cambiaron, titulo=f"{len(cambiaron)} órdenes recibieron respuestas distintas")
    else:
        p.nota("Ninguna orden cambió de equipo entre corridas.", "info")
    return corridas


# ------------------------------------------------------------------ comparar y exportar

@_amable
def tabla_comparacion(conjunto: Conjunto, ejemplos: int = 10, llm_resultado: Clasificacion | None = None) -> None:
    """Las tres arquitecturas y el LLM lado a lado: aciertos, trampas, costo, tiempo, privacidad y explicabilidad."""
    ejemplos = _validar_cantidad(ejemplos, conjunto)
    filas = []
    for clave in ARQUITECTURAS:
        c = _entrenar_y_clasificar(conjunto, clave, ejemplos)
        filas.append({"método": c.metodo, "ejemplos etiquetados": c.ejemplos * len(conjunto.clases),
                      "aciertos en prueba": f"{c.aciertos()} de {c.total()}",
                      "trampas y controles": f"{c.aciertos('trampa')} de {c.total('trampa')}" if c.total("trampa") else "—",
                      "US$ por 1000 órdenes": "0 (su CPU)",
                      "tiempo por orden": _tiempo_por_orden(c),
                      "¿salen los textos?": "no", "explicabilidad": EXPLICABILIDAD[c.metodo]})
    if llm_resultado is not None:
        c = llm_resultado
        por_mil = _costo_por_mil(c)
        filas.append({"método": f"LLM · {c.modelo}", "ejemplos etiquetados": 0,
                      "aciertos en prueba": f"{c.aciertos()} de {c.total()}",
                      "trampas y controles": f"{c.aciertos('trampa')} de {c.total('trampa')}" if c.total("trampa") else "—",
                      "US$ por 1000 órdenes": "0 (su CPU)" if c.proveedor == "ollama" else
                      (_n(por_mil, 3) if por_mil is not None else "sin precio"),
                      "tiempo por orden": f"{_n(sum(c.tiempos) / len(c.tiempos), 2)} s",
                      "¿salen los textos?": "no (modelo local)" if c.proveedor == "ollama" else
                      ("sí: a los servidores del proveedor" if c.proveedor != "grabado"
                       else "sí con la API; en esta sesión, no (respuestas grabadas)"),
                      "explicabilidad": EXPLICABILIDAD["LLM"]})
    p.mostrar_tabla(filas, titulo=f"Comparación · {ejemplos} ejemplos por {conjunto.palabra_clase} para las arquitecturas")


def _tiempo_por_orden(c: Clasificacion) -> str:
    """Lo que tarda en clasificar una orden ya entrenada, medido otra vez y sin vectores guardados."""
    textos = c.textos
    guardados = {t: _GRANITE.get("vectores", {}).pop(t) for t in textos if t in _GRANITE.get("vectores", {})}
    inicio = time.perf_counter()
    c.modelo_entrenado.predecir(textos)
    ms = 1000 * (time.perf_counter() - inicio) / len(textos)
    _GRANITE.get("vectores", {}).update(guardados)
    return "menos de 1 ms" if ms < 1 else f"{_n(ms, 0)} ms"


COLUMNAS_CSV = ["sesion", "laboratorio", "pareja", "fecha", "tarea", "instancia", "metodo", "estrategia", "proveedor",
                "modelo", "correcto", "resultado", "iteraciones", "llamadas", "tokens_entrada", "tokens_salida",
                "tokens_razonamiento", "costo_usd", "tiempo_s", "notas"]


def exportar_csv(pareja: str, ruta: str = ARCHIVO_CSV) -> Path | None:
    """Escribe en el CSV común del contrapunto todas las clasificaciones de esta sesión del kernel."""
    if not _REGISTRO:
        p.nota("No hay resultados para exportar: ejecute antes las secciones 2 a 7.", "aviso")
        return None
    if not isinstance(pareja, str) or not pareja.strip() or pareja.strip() == "Nombre 1 y Nombre 2":
        p.nota("Escriba los nombres de la pareja en PAREJA para que el CSV sea suyo.", "aviso")
    destino = Path(ruta)
    try:
        with destino.open("w", newline="", encoding="utf-8") as f:
            escritor = csv.DictWriter(f, fieldnames=COLUMNAS_CSV)
            escritor.writeheader()
            for fila in _REGISTRO.values():
                escritor.writerow({**fila, "pareja": pareja})
    except PermissionError:
        p.nota(f"No pude escribir {destino}: ciérrelo si está abierto en Excel y ejecute de nuevo.", "error")
        return None
    grupos = {}
    for fila in _REGISTRO.values():
        g = grupos.setdefault((fila["metodo"], fila["estrategia"]), {"filas": 0, "aciertos": 0, "costo": 0.0})
        g["filas"] += 1
        g["aciertos"] += fila["correcto"]
        g["costo"] += float(fila["costo_usd"] or 0)
    orden = lambda clave: (clave[0] == "LLM", clave[0], int(re.match(r"\d*", clave[1]).group() or 0), clave[1])
    p.mostrar_tabla([{"método": m, "estrategia": e, "filas (prueba y trampas)": g["filas"],
                      "aciertos (prueba y trampas)": g["aciertos"], "costo (US$)": _n(g["costo"], 5)}
                     for (m, e), g in sorted(grupos.items(), key=lambda x: orden(x[0]))],
                    titulo=f"{len(_REGISTRO)} filas guardadas en {destino}")
    return destino


def avisar_privacidad(enviar: bool, llm=None) -> bool:
    """Antes de enviar textos propios a un LLM, recuerda que no deben tener datos personales ni información confidencial."""
    if not enviar:
        p.nota("No se envió ningún texto al LLM. Para hacerlo, cambie ENVIAR_AL_LLM a True.", "info")
        return False
    if llm is not None and llm.proveedor == "grabado":
        p.nota("Con respuestas grabadas no hay respuestas para sus textos. Para clasificarlos con un LLM, configure una "
               "clave de API o Ollama en la sección 0.2, o use el chat del LLM, como dice el enunciado del TI-2.", "aviso")
        return False
    p.nota("Con la vía API, cada texto sale de su computador hacia los servidores del proveedor. Envíe solo textos sin datos "
           "personales (nombres, documentos, teléfonos, correos, direcciones) ni información confidencial de su "
           "organización. Con la vía local, nada sale de su computador.", "aviso", "Antes de enviar")
    return True
