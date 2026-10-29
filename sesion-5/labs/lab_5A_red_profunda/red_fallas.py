"""La red neuronal del Laboratorio 5A (Sesión 5 de Sistemas Inteligentes): predecir la falla de una máquina.

Reúne lo que el notebook necesita:
- los datos del AI4I 2020, separados en entrenamiento, validación y prueba;
- un perceptrón multicapa en PyTorch, con las capas, las neuronas y el dropout que elija la pareja;
- el entrenamiento por minilotes con Adam, con parada temprana opcional;
- las comparaciones de las secciones 3 a 6, la mirada a la retropropagación y la evaluación final;
- la bitácora resultados_5A.csv, con una fila por cada red entrenada.

Todo corre en la CPU. Los errores de configuración se muestran en español, en una caja roja, sin traza.
"""
from __future__ import annotations

import copy
import csv
import platform
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import numpy as np

import graficas
import presentacion as p

ARCHIVO_DATOS = Path("datos") / "ai4i2020.csv"
BITACORA = Path("resultados_5A.csv")
SEMILLA = 7
LOTE = 400                       # registros por minilote: cada paso de Adam usa 400 registros
# Las cinco lecturas de la máquina y el tipo de producto, que entra como tres columnas (H, L y M)
LECTURAS = ["Air temperature [K]", "Process temperature [K]", "Rotational speed [rpm]", "Torque [Nm]", "Tool wear [min]"]
TIPOS = ["H", "L", "M"]
NOMBRES_ENTRADAS = ["temperatura del aire", "temperatura del proceso", "velocidad de giro", "torque",
                    "desgaste de la herramienta", "tipo H", "tipo L", "tipo M"]
EXCLUIDAS = {"UDI": "el número de fila", "Product ID": "el código de la pieza",
             "TWF": "falla por desgaste de la herramienta", "HDF": "falla por disipación de calor",
             "PWF": "falla de potencia", "OSF": "falla por sobreesfuerzo", "RNF": "falla aleatoria"}
# La configuración de la diapositiva 10 de la charla inicial (ejemplos/curvas_5a.py)
DIAPOSITIVA_10 = {"capas": (128, 128, 128), "registros": 400, "tasa": 0.001, "epocas": 300}


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


def _n(valor, decimales: int = 0) -> str:
    """Número en formato español: espacio para los miles y coma decimal."""
    return f"{valor:,.{decimales}f}".replace(",", " ").replace(".", ",")


def _pct(fraccion, decimales: int = 1) -> str:
    return f"{_n(100 * fraccion, decimales)} %"


def _tasa_texto(tasa) -> str:
    """La tasa como se escribe en el código: 0.001, 0.00001."""
    return np.format_float_positional(tasa, trim="-")


def _torch():
    try:
        import torch
    except ImportError:
        intel = platform.system() == "Darwin" and platform.machine() == "x86_64"
        raise ErrorDeLaboratorio(
            "No está instalada la librería torch, que entrena la red. "
            + ("En un Mac con procesador Intel no hay torch para Python 3.13: use el respaldo en Google Colab (sección 0)."
               if intel else "Ejecute la primera celda del notebook y reinicie el kernel.")) from None
    return torch


# ------------------------------------------------------------------ validación de la configuración

def _coma(valor, nombre: str, ejemplo: str) -> None:
    """Una coma decimal convierte 0,3 en la pareja (0, 3): se reconoce y se explica."""
    if isinstance(valor, tuple) and len(valor) == 2 and all(isinstance(v, int) for v in valor):
        raise ErrorDeLaboratorio(f"{nombre} {valor[0]},{valor[1]} lleva coma: en el código, los decimales se escriben con "
                                 f"punto. Escriba {valor[0]}.{valor[1]}, como en {ejemplo}.")


def _validar_capas(capas, nombre: str = "CAPAS") -> tuple:
    if isinstance(capas, bool) or isinstance(capas, (int, float)):
        raise ErrorDeLaboratorio(f"{nombre} es una lista entre corchetes, con las neuronas de cada capa oculta: por ejemplo "
                                 f"[64, 64] (escribió {capas!r}).")
    if not isinstance(capas, (list, tuple)) or not capas:
        raise ErrorDeLaboratorio(f"{nombre} necesita al menos una capa oculta, entre corchetes: por ejemplo [64, 64].")
    if len(capas) > 6:
        raise ErrorDeLaboratorio(f"{nombre} tiene {len(capas)} capas ocultas. Para este laboratorio, use de 1 a 6.")
    for n in capas:
        if isinstance(n, (list, tuple)):
            raise ErrorDeLaboratorio(f"Sobra o falta un corchete en {nombre}: encontré una lista dentro de otra ({n!r}). "
                                     "Compare con la celda original: cada red es una lista de números, como [64, 64].")
        if isinstance(n, bool) or not isinstance(n, int) or not 1 <= n <= 1024:
            raise ErrorDeLaboratorio(f"En {nombre}, cada capa es un número entero de neuronas, entre 1 y 1024, sin comillas "
                                     f"ni decimales (encontré {n!r}).")
    return tuple(capas)


def _validar_dropout(dropout, nombre: str = "DROPOUT") -> float:
    _coma(dropout, f"El dropout", "0.3")
    if isinstance(dropout, bool) or not isinstance(dropout, (int, float)) or not 0 <= dropout <= 0.9:
        raise ErrorDeLaboratorio(f"{nombre} es la fracción de neuronas que se apagan en cada paso: un número entre 0 y 0.9, "
                                 f"por ejemplo 0.3 (escribió {dropout!r}).")
    return float(dropout)


def _validar_tasa(tasa, nombre: str = "TASA") -> float:
    _coma(tasa, "La tasa", "0.001")
    if isinstance(tasa, bool) or not isinstance(tasa, (int, float)):
        raise ErrorDeLaboratorio(f"{nombre} es un número sin comillas, por ejemplo 0.001 (escribió {tasa!r}).")
    if tasa == 0:
        raise ErrorDeLaboratorio(f"Una tasa de aprendizaje de 0 no mueve los pesos. Si escribió 0,1 o 1,0 dentro de una lista, "
                                 "Python leyó dos números separados por la coma: escriba 0.1 o 1.0, con punto.")
    if not 0 < tasa <= 10:
        raise ErrorDeLaboratorio(f"{nombre} va entre 0.000001 y 10 (escribió {tasa!r}).")
    return float(tasa)


def _validar_entero(valor, nombre: str, minimo: int, maximo: int, ejemplo) -> int:
    if isinstance(valor, bool) or not isinstance(valor, int) or not minimo <= valor <= maximo:
        raise ErrorDeLaboratorio(f"{nombre} es un número entero entre {minimo} y {maximo}, sin comillas ni decimales, por "
                                 f"ejemplo {ejemplo} (escribió {valor!r}).")
    return valor


def _validar_paciencia(paciencia, nombre: str = "la paciencia") -> int | None:
    if paciencia is None:
        return None
    return _validar_entero(paciencia, nombre, 1, 500, 20)


# ------------------------------------------------------------------ los datos

@dataclass
class Datos:
    x: np.ndarray                   # las 8 entradas de los 10 000 registros
    y: np.ndarray                   # 1 si la máquina falló
    filas: list                     # los registros originales, para mostrarlos
    entrenamiento: np.ndarray       # índices disponibles para entrenar (5000), en orden fijo
    validacion: np.ndarray          # 3000 índices
    prueba: np.ndarray              # 2000 índices, que se miran una sola vez

    def fallas(self, indices) -> int:
        return int(self.y[indices].sum())


@_amable
def cargar_datos(ruta=ARCHIVO_DATOS, mostrar: bool = True) -> Datos | None:
    """Lee el AI4I 2020, arma las 8 entradas y separa los registros en entrenamiento, validación y prueba."""
    ruta = Path(ruta)
    if not ruta.exists():
        raise ErrorDeLaboratorio(f"No encuentro {ruta}. Abra el notebook desde la carpeta del laboratorio, donde está la "
                                 "carpeta datos/, y reinicie el kernel.")
    with ruta.open(encoding="utf-8-sig", newline="") as f:
        filas = list(csv.DictReader(f))
    x = np.array([[float(r[c]) for c in LECTURAS] + [float(r["Type"] == t) for t in TIPOS] for r in filas])
    y = np.array([float(r["Machine failure"]) for r in filas])
    # La misma permutación de ejemplos/curvas_5a.py: los primeros 400 de entrenamiento y los 3000 de validación son los
    # de las diapositivas 10 y 11 de la charla inicial
    orden = np.random.default_rng(SEMILLA).permutation(len(filas))
    datos = Datos(x, y, filas, entrenamiento=np.concatenate([orden[:400], orden[5400:]]),
                  validacion=orden[400:3400], prueba=orden[3400:5400])
    if mostrar:
        graficas.primeras_filas(filas, LECTURAS)
        p.nota(f"{_n(len(filas))} registros, de los cuales {_n(int(y.sum()))} son fallas ({_pct(y.mean(), 2)}). "
               f"La red usa 8 entradas: las 5 lecturas y el tipo de producto en tres columnas (H, L y M).", "info",
               "El conjunto")
    return datos


def mostrar_separacion(datos: Datos) -> None:
    """Muestra cuántos registros y fallas hay en cada parte, y lo que lograría responder siempre «no falla»."""
    filas = []
    for nombre, idx, uso in (("entrenamiento", datos.entrenamiento, "la red aprende sus pesos con ellos"),
                             ("validación", datos.validacion, "para comparar configuraciones y decidir cuándo parar"),
                             ("prueba", datos.prueba, "se mira una sola vez, al final (sección 7.2)")):
        filas.append({"parte": nombre, "registros": _n(len(idx)), "fallas": datos.fallas(idx),
                      "proporción de fallas": _pct(datos.fallas(idx) / len(idx)), "para qué": uso})
    p.mostrar_tabla(filas, titulo="Las tres partes de los datos")
    base = 1 - datos.fallas(datos.validacion) / len(datos.validacion)
    p.nota(f"Una «red» que responda siempre «no falla» acierta el {_pct(base, 2)} de los registros de validación, sin "
           f"detectar ninguna de sus {datos.fallas(datos.validacion)} fallas. Es la exactitud que hay que superar, y por eso "
           "la exactitud sola no basta: hay que mirar cuántas fallas detecta la red.", "aviso", "La línea base")


def perdida_constante(datos: Datos) -> float:
    """La pérdida de validación de una «red» que da a todo registro la probabilidad de falla del entrenamiento."""
    q = datos.fallas(datos.entrenamiento) / len(datos.entrenamiento)
    f = datos.fallas(datos.validacion) / len(datos.validacion)
    return float(-(f * np.log(q) + (1 - f) * np.log(1 - q)))


# ------------------------------------------------------------------ la red y el entrenamiento

@dataclass
class Resultado:
    nombre: str
    capas: tuple
    dropout: float
    tasa: float
    epocas: int
    registros: int
    paciencia: int | None
    perdida_entrenamiento: list = field(default_factory=list)   # una por época
    perdida_validacion: list = field(default_factory=list)      # una por época
    pasos_validacion: list = field(default_factory=list)        # una por paso (solo en la sección 3)
    pasos_por_epoca: int = 1
    mejor_epoca: int = 0
    epoca_guardada: int = 0         # la época de la red que queda: la última, o la mejor si hubo parada temprana
    segundos: float = 0.0
    parametros: int = 0
    desbordada: bool = False        # la pérdida se volvió infinita
    red: object = field(default=None, repr=False)
    media: np.ndarray = field(default=None, repr=False)
    desviacion: np.ndarray = field(default=None, repr=False)
    vp: int = 0                     # fallas detectadas en validación
    fn: int = 0                     # fallas que la red no vio
    fp: int = 0                     # falsas alarmas
    vn: int = 0

    @property
    def exactitud(self) -> float:
        return (self.vp + self.vn) / max(1, self.vp + self.vn + self.fp + self.fn)

    @property
    def perdida_guardada(self) -> float:
        return self.perdida_validacion[self.epoca_guardada - 1] if self.perdida_validacion else float("nan")

    @property
    def config(self) -> tuple:
        return (self.capas, self.dropout, self.tasa, self.epocas, self.registros, self.paciencia)


_HECHOS: dict = {}          # cada configuración ya entrenada en esta sesión del kernel, para no repetirla


def _construir(capas, dropout, torch):
    """El perceptrón multicapa: por cada capa oculta, Linear, ReLU y Dropout; al final, una neurona de salida."""
    from torch import nn
    torch.manual_seed(SEMILLA)          # pesos iniciales reproducibles
    partes, entradas = [], len(NOMBRES_ENTRADAS)
    for n in capas:
        partes += [nn.Linear(entradas, n), nn.ReLU(), nn.Dropout(dropout)]
        entradas = n
    return nn.Sequential(*partes, nn.Linear(entradas, 1))


def _tensores(datos, indices, media, desviacion, torch, tipo=None):
    tipo = tipo or torch.float32
    x = torch.tensor((datos.x[indices] - media) / desviacion, dtype=tipo)
    y = torch.tensor(datos.y[indices, None], dtype=tipo)
    return x, y


def _entrenar(datos: Datos, capas, dropout, tasa, epocas, registros, paciencia, por_paso=False, nombre="") -> Resultado:
    """Entrena una red con minilotes de 400 registros y Adam; mide la pérdida de entrenamiento y de validación por época."""
    torch = _torch()
    from torch import nn
    clave = (capas, dropout, tasa, epocas, registros, paciencia, por_paso)
    if clave in _HECHOS:
        anterior = copy.copy(_HECHOS[clave])
        anterior.nombre = nombre or anterior.nombre
        return anterior
    indices = datos.entrenamiento[:registros]
    # Estandarizar: cada entrada queda con promedio 0 y desviación 1, medidos en los registros de entrenamiento
    media, desviacion = datos.x[indices].mean(0), datos.x[indices].std(0) + 1e-9
    x_e, y_e = _tensores(datos, indices, media, desviacion, torch)
    x_v, y_v = _tensores(datos, datos.validacion, media, desviacion, torch)
    red = _construir(capas, dropout, torch)
    optimizador = torch.optim.Adam(red.parameters(), lr=tasa)
    perdida = nn.BCEWithLogitsLoss()
    azar = np.random.default_rng(SEMILLA)       # el orden de los minilotes, también reproducible
    r = Resultado(nombre, capas, dropout, tasa, epocas, registros, paciencia,
                  parametros=sum(w.numel() for w in red.parameters()), media=media, desviacion=desviacion)
    r.pasos_por_epoca = -(-registros // LOTE)
    mejor, estado = float("inf"), None
    inicio = time.perf_counter()
    for epoca in range(1, epocas + 1):
        red.train()
        orden = np.arange(registros) if LOTE >= registros else azar.permutation(registros)
        for i in range(0, registros, LOTE):
            lote = orden[i:i + LOTE]
            optimizador.zero_grad()
            error = perdida(red(x_e[lote]), y_e[lote])
            error.backward()            # la retropropagación: la culpa de cada peso
            optimizador.step()          # un paso cuesta abajo
            if por_paso:
                red.eval()
                with torch.no_grad():
                    r.pasos_validacion.append(float(perdida(red(x_v), y_v)))
                red.train()
        red.eval()
        with torch.no_grad():
            r.perdida_entrenamiento.append(float(perdida(red(x_e), y_e)))
            r.perdida_validacion.append(float(perdida(red(x_v), y_v)))
        if not np.isfinite(r.perdida_validacion[-1]):
            r.desbordada = True
            break
        if r.perdida_validacion[-1] < mejor:
            mejor, r.mejor_epoca = r.perdida_validacion[-1], epoca
            if paciencia:
                estado = {k: v.clone() for k, v in red.state_dict().items()}
        if paciencia and epoca - r.mejor_epoca >= paciencia:
            break
    r.segundos = time.perf_counter() - inicio
    r.epoca_guardada = len(r.perdida_validacion)
    if paciencia and estado is not None:            # parada temprana: se queda la red de la mejor época
        red.load_state_dict(estado)
        r.epoca_guardada = r.mejor_epoca
    r.red = red
    with torch.no_grad():
        prediccion = (red(x_v) > 0).numpy().ravel()     # salida positiva = probabilidad de falla mayor que 0,5
    real = datos.y[datos.validacion] == 1
    r.vp, r.fn = int((prediccion & real).sum()), int((~prediccion & real).sum())
    r.fp, r.vn = int((prediccion & ~real).sum()), int((~prediccion & ~real).sum())
    _HECHOS[clave] = r
    _anotar(r)
    return r


def _anotar(r: Resultado, parte: str = "validación") -> None:
    """Agrega o actualiza la fila de esta red en la bitácora resultados_5A.csv."""
    columnas = ["fecha", "nombre", "capas", "dropout", "tasa", "epocas", "registros", "paciencia", "epocas_corridas",
                "epoca_guardada", "perdida_entrenamiento", "perdida_validacion", "parte_evaluada", "exactitud",
                "fallas_detectadas", "fallas_reales", "falsas_alarmas", "parametros", "segundos"]
    fila = {"fecha": date.today().isoformat(), "nombre": r.nombre, "capas": str(list(r.capas)), "dropout": r.dropout,
            "tasa": _tasa_texto(r.tasa), "epocas": r.epocas, "registros": r.registros,
            "paciencia": r.paciencia if r.paciencia else "", "epocas_corridas": len(r.perdida_validacion),
            "epoca_guardada": r.epoca_guardada,
            "perdida_entrenamiento": round(r.perdida_entrenamiento[r.epoca_guardada - 1], 4) if r.perdida_entrenamiento else "",
            "perdida_validacion": round(r.perdida_guardada, 4), "parte_evaluada": parte,
            "exactitud": round(r.exactitud, 4), "fallas_detectadas": r.vp, "fallas_reales": r.vp + r.fn,
            "falsas_alarmas": r.fp, "parametros": r.parametros, "segundos": round(r.segundos, 2)}
    existentes = []
    if BITACORA.exists():
        try:
            with BITACORA.open(encoding="utf-8", newline="") as f:
                existentes = list(csv.DictReader(f))
        except (OSError, csv.Error):
            existentes = []
    clave = lambda d: tuple(str(d.get(k, "")) for k in ("nombre", "capas", "dropout", "tasa", "epocas", "registros",
                                                         "paciencia", "parte_evaluada"))
    existentes = [d for d in existentes if clave(d) != clave(fila)] + [fila]
    try:
        with BITACORA.open("w", encoding="utf-8", newline="") as f:
            escritor = csv.DictWriter(f, fieldnames=columnas, extrasaction="ignore")
            escritor.writeheader()
            escritor.writerows(existentes)
    except PermissionError:
        p.nota(f"No pude escribir {BITACORA}: ciérrelo si está abierto en Excel. La red sí se entrenó.", "aviso")


# ------------------------------------------------------------------ sección 2: la primera red

@_amable
def entrenar(datos: Datos, capas=(64, 64), dropout=0.3, tasa=0.001, epocas=60, registros=5000, paciencia=None,
             nombre: str = "red", mostrar: bool = True) -> Resultado | None:
    """Entrena una red con la configuración dada y muestra su código en PyTorch y sus curvas de aprendizaje."""
    if datos is None:
        raise ErrorDeLaboratorio("Primero ejecute la celda que carga los datos (sección 1).")
    capas = _validar_capas(capas)
    dropout = _validar_dropout(dropout)
    tasa = _validar_tasa(tasa)
    epocas = _validar_entero(epocas, "EPOCAS", 1, 1000, 60)
    registros = _validar_entero(registros, "REGISTROS", 50, len(datos.entrenamiento), 400)
    paciencia = _validar_paciencia(paciencia)
    r = _entrenar(datos, capas, dropout, tasa, epocas, registros, paciencia, nombre=nombre)
    if mostrar:
        graficas.codigo_red(capas, dropout, r.parametros)
        graficas.curvas(r, f"{nombre} · {len(r.perdida_validacion)} épocas en {_n(r.segundos, 1)} s")
        if r.desbordada:
            p.nota("La pérdida se volvió infinita: los pasos son tan grandes que los pesos se desbocaron. Baje la tasa de "
                   "aprendizaje.", "error", "La red se desbocó")
    return r


@_amable
def matriz(r: Resultado, datos: Datos) -> None:
    """La matriz de confusión en validación, junto a lo que lograría responder siempre «no falla»."""
    if r is None:
        raise ErrorDeLaboratorio("La red no se entrenó: revise el mensaje de arriba, corrija la celda y ejecútela de nuevo.")
    base = 1 - datos.fallas(datos.validacion) / len(datos.validacion)
    graficas.matriz_fallas(r.vp, r.fn, r.fp, r.vn, f"Matriz de confusión en validación · {r.nombre}")
    tipo = "exito" if r.vp else "aviso"
    p.nota(f"Exactitud: {_pct(r.exactitud, 2)}, frente a {_pct(base, 2)} de responder siempre «no falla». "
           f"La red detectó {r.vp} de las {r.vp + r.fn} fallas reales y dio {r.fp} falsas alarmas.", tipo, "Lo que hizo la red")


# ------------------------------------------------------------------ sección 3: la tasa de aprendizaje

@_amable
def comparar_tasas(datos: Datos, tasas, capas=(64, 64), dropout=0.3, epocas=60) -> list | None:
    """Entrena la misma red con cada tasa de aprendizaje y dibuja la pérdida de validación después de cada paso."""
    if not isinstance(tasas, (list, tuple)):
        raise ErrorDeLaboratorio("TASAS es una lista entre corchetes, por ejemplo [0.00001, 0.001, 1.0].")
    if not tasas:
        raise ErrorDeLaboratorio("TASAS está vacía: escriba entre los corchetes las tasas que quiere comparar.")
    if len(tasas) > 5:
        raise ErrorDeLaboratorio("Compare como máximo 5 tasas a la vez, para que la gráfica se lea.")
    tasas = [_validar_tasa(t, "Cada tasa de TASAS") for t in tasas]
    capas, dropout = _validar_capas(capas), _validar_dropout(dropout)
    epocas = _validar_entero(epocas, "EPOCAS", 1, 1000, 60)
    resultados = [_entrenar(datos, capas, dropout, t, epocas, len(datos.entrenamiento), None, por_paso=True,
                            nombre=f"tasa {_tasa_texto(t)}") for t in sorted(set(tasas))]
    constante = perdida_constante(datos)
    graficas.curvas_tasas(resultados, constante)
    p.mostrar_tabla([{"tasa": _tasa_texto(r.tasa),
                      "pérdida de validación al final": _n(r.perdida_validacion[-1], 3) if not r.desbordada else "infinita",
                      "la más alta en el camino": _n(max(r.pasos_validacion), 2) if r.pasos_validacion else "—",
                      "fallas detectadas": f"{r.vp} de {r.vp + r.fn}", "falsas alarmas": r.fp,
                      "tiempo": f"{_n(r.segundos, 1)} s"} for r in resultados],
                    titulo=f"Las tasas, lado a lado (pérdida de responder siempre «no falla»: {_n(constante, 3)})")
    _revisar_tasas([r.tasa for r in resultados])
    return resultados


def _revisar_tasas(tasas) -> None:
    pequena, grande = min(tasas) <= 0.0001, max(tasas) >= 0.1
    if len(tasas) >= 3 and pequena and grande:
        p.nota("Hay una tasa muy pequeña, una intermedia y una muy grande. Anote en la tabla de abajo qué hizo cada una.",
               "exito", "✓ Tres comportamientos para comparar")
        return
    faltan = []
    if not pequena:
        faltan.append("una muy pequeña, como 0.00001")
    if not grande:
        faltan.append("una muy grande, como 1.0")
    if len(tasas) < 3 and not faltan:
        faltan.append("una intermedia, como 0.001")
    p.nota("Para ver los tres comportamientos, agregue a TASAS " + ", y ".join(faltan) + ", y ejecute de nuevo. "
           "Las tasas ya entrenadas no se vuelven a entrenar.", "aviso", "Falta una tasa")


# ------------------------------------------------------------------ secciones 4 y 5: memorizar y frenar

@_amable
def comprobar_sobreajuste(r: Resultado) -> None:
    """Dice si las curvas de entrenamiento y de validación se separaron, y si es la configuración de la diapositiva 10."""
    if r is None:
        raise ErrorDeLaboratorio("La red no se entrenó: revise el mensaje de arriba, corrija la celda y ejecútela de nuevo.")
    minimo = min(r.perdida_validacion)
    subida = r.perdida_validacion[-1] - minimo
    brecha = r.perdida_validacion[-1] - r.perdida_entrenamiento[-1]
    if subida > 0.05 and brecha > 0.1:
        p.nota(f"La pérdida de validación tocó su mínimo ({_n(minimo, 3)}) en la época {r.mejor_epoca} y terminó en "
               f"{_n(r.perdida_validacion[-1], 3)}, mientras la de entrenamiento bajó a "
               f"{'casi cero' if r.perdida_entrenamiento[-1] < 0.001 else _n(r.perdida_entrenamiento[-1], 3)}. "
               "Las curvas se separaron: la red memorizó.", "exito", "✓ Hay sobreajuste")
    else:
        p.nota(f"La pérdida de validación terminó en {_n(r.perdida_validacion[-1], 3)}, a {_n(subida, 3)} de su mínimo, y la "
               f"de entrenamiento en {_n(r.perdida_entrenamiento[-1], 3)}: las curvas no se separaron mucho. Baje REGISTROS "
               "(por ejemplo a 400) y agrande la red (por ejemplo [128, 128, 128]), y ejecute de nuevo.", "aviso",
               "Todavía no memoriza")
    if (r.capas, r.registros, r.tasa, r.epocas) == tuple(DIAPOSITIVA_10.values()) and r.dropout == 0:
        p.nota("Si vio la charla inicial: es la misma red, con los mismos datos y la misma semilla, de la diapositiva "
               "«Memorizar no es aprender», donde el mínimo de validación es 0,133 en la época 93 y la pérdida termina en "
               "0,390. En otro computador, los decimales pueden variar un poco. Si no la vio, puede ignorar esta nota.",
               "info", "La misma red de la charla")


@_amable
def comparar_frenos(datos: Datos, base: Resultado, dropout=0.3, paciencias=()) -> list | None:
    """Sobre el caso de la sección 4: la misma red con dropout, y con parada temprana para cada paciencia."""
    if base is None:
        raise ErrorDeLaboratorio("Primero entrene la red de la sección 4: esta sección le pone frenos a esa misma red.")
    dropout = _validar_dropout(dropout, "DROPOUT_FRENO")
    if not isinstance(paciencias, (list, tuple)):
        raise ErrorDeLaboratorio("PACIENCIAS es una lista entre corchetes, por ejemplo [20, 50].")
    if len(paciencias) > 4:
        raise ErrorDeLaboratorio("Compare como máximo 4 paciencias a la vez.")
    paciencias = sorted({_validar_paciencia(v, "Cada paciencia de PACIENCIAS") for v in paciencias})
    if dropout == 0 and not paciencias:
        p.nota("Sin dropout ni paciencias no hay frenos que comparar: escriba DROPOUT_FRENO = 0.3 y, en PACIENCIAS, "
               "por ejemplo [20, 50].", "aviso", "Faltan los frenos")
    con_dropout = _entrenar(datos, base.capas, dropout, base.tasa, base.epocas, base.registros, None,
                            nombre=f"memorizar + dropout {dropout}") if dropout > 0 else None
    paradas = [_entrenar(datos, base.capas, dropout, base.tasa, base.epocas, base.registros, v,
                         nombre=f"memorizar + dropout {dropout} + paciencia {v}") for v in paciencias]
    graficas.curvas_frenos(base, con_dropout, paradas)
    filas = [{"freno": "referencia: responder siempre «no falla»", "épocas que corrió": "—", "época de la red que queda": "—",
              "pérdida de validación de esa red": _n(perdida_constante(datos), 3),
              "fallas detectadas": f"0 de {datos.fallas(datos.validacion)}"}]
    for r, freno in [(base, "ninguno")] + ([(con_dropout, f"dropout {dropout:g}")] if con_dropout else []) + \
            [(r, (f"dropout {dropout:g} y " if dropout else "") + f"paciencia {r.paciencia}") for r in paradas]:
        filas.append({"freno": freno, "épocas que corrió": len(r.perdida_validacion),
                      "época de la red que queda": r.epoca_guardada,
                      "pérdida de validación de esa red": _n(r.perdida_guardada, 3),
                      "fallas detectadas": f"{r.vp} de {r.vp + r.fn}"})
    p.mostrar_tabla(filas, titulo="Los frenos frente a la red sin frenos de la sección 4")
    return [base, con_dropout, *paradas]


# ------------------------------------------------------------------ sección 6: profundidad y anchura

@_amable
def comparar_redes(datos: Datos, redes, dropout=0.3, tasa=0.001, epocas=100) -> list | None:
    """Entrena cada red de la lista con los mismos datos y muestra una tabla con su desempeño, su tamaño y su tiempo."""
    if not isinstance(redes, list) or not redes or not all(isinstance(r, list) for r in redes):
        raise ErrorDeLaboratorio("Sobra o falta un corchete en REDES. REDES empieza con [ y termina con ], y cada red "
                                 "va entre sus propios corchetes, separada por una coma: [[16], [64, 64], [128, 128, 128]]. "
                                 "Compare con la celda original.")
    if len(redes) > 6:
        raise ErrorDeLaboratorio("Compare como máximo 6 redes a la vez.")
    redes = [_validar_capas(r, f"la red {r}") for r in redes]
    dropout, tasa = _validar_dropout(dropout), _validar_tasa(tasa)
    epocas = _validar_entero(epocas, "EPOCAS_REDES", 1, 1000, 100)
    resultados = [_entrenar(datos, r, dropout, tasa, epocas, len(datos.entrenamiento), None, nombre=f"red {list(r)}")
                  for r in dict.fromkeys(redes)]
    p.mostrar_tabla([{"red (neuronas por capa oculta)": str(list(r.capas)), "capas ocultas": len(r.capas),
                      "parámetros": _n(r.parametros), "exactitud": _pct(r.exactitud, 2),
                      "fallas detectadas": f"{r.vp} de {r.vp + r.fn}", "falsas alarmas": r.fp,
                      "pérdida de validación": _n(r.perdida_validacion[-1], 3), "tiempo": f"{_n(r.segundos, 1)} s"}
                     for r in resultados],
                    titulo=f"Redes de distinta profundidad y anchura · dropout {dropout:g}, tasa {_tasa_texto(tasa)}, "
                           f"{epocas} épocas")
    graficas.curvas_redes(resultados)
    if len(resultados) < 4:
        p.nota("Agregue a REDES una red propia, más ancha, más profunda o más pequeña, y ejecute de nuevo: las redes ya "
               "entrenadas no se repiten.", "aviso", "Falta su red")
    return resultados


# ------------------------------------------------------------------ sección 7: para casa

@_amable
def mirar_retropropagacion(datos: Datos, tasa: float = 0.1) -> None:
    """Un paso de entrenamiento por dentro: la culpa que PyTorch asigna a algunos pesos, comprobada midiendo la pendiente."""
    torch = _torch()
    from torch import nn
    indices = datos.entrenamiento[:LOTE]
    media, desviacion = datos.x[indices].mean(0), datos.x[indices].std(0) + 1e-9
    x, y = _tensores(datos, indices, media, desviacion, torch, torch.float64)
    red = _construir((64, 64), 0.0, torch).double().eval()
    perdida = nn.BCEWithLogitsLoss()
    error = perdida(red(x), y)
    error.backward()                    # PyTorch reparte la culpa a los 4 801 pesos de una vez
    capas = [m for m in red if isinstance(m, nn.Linear)]
    elegidos = [(capas[0].weight, (0, 3), "capa oculta 1, de «torque» a la neurona 1"),
                (capas[0].weight, (0, 4), "capa oculta 1, de «desgaste» a la neurona 1"),
                (capas[1].weight, (0, 0), "capa oculta 2, de la neurona 1 a la neurona 1"),
                (capas[2].weight, (0, 0), "salida, de la neurona 1 de la capa 2 a «¿falla?»"),
                (capas[2].bias, (0,), "salida, el sesgo de «¿falla?»")]
    h = 1e-6                            # un movimiento tan pequeño que ninguna ReLU cambia de lado
    filas = []
    with torch.no_grad():
        for peso, donde, descripcion in elegidos:
            original = float(peso[donde])
            peso[donde] = original + h
            arriba = float(perdida(red(x), y))
            peso[donde] = original - h
            abajo = float(perdida(red(x), y))
            peso[donde] = original
            medida = (arriba - abajo) / (2 * h)
            culpa = float(peso.grad[donde])
            filas.append({"peso": descripcion, "valor": _n(original, 4), "culpa según PyTorch": f"{culpa:+.6f}".replace(".", ","),
                          "pendiente medida": f"{medida:+.6f}".replace(".", ","),
                          f"valor después del paso (tasa {tasa:g})": _n(original - tasa * culpa, 4)})
        antes = float(error)
        for w in red.parameters():          # un paso del descenso de gradiente simple, con todos los pesos
            w -= tasa * w.grad
        despues = float(perdida(red(x), y))
    p.mostrar_tabla(filas, titulo=f"Un minilote de {LOTE} registros · pérdida {_n(antes, 4)}")
    p.nota(f"Después de mover los 4 801 pesos un paso en contra de su culpa, la pérdida de ese minilote pasó de "
           f"{_n(antes, 4)} a {_n(despues, 4)}.", "exito" if despues < antes else "aviso", "Un paso cuesta abajo")


_EVALUADAS_EN_PRUEBA: list = []


@_amable
def evaluar_en_prueba(datos: Datos, capas, dropout, tasa, epocas, paciencia=None, evaluar: bool = True) -> Resultado | None:
    """Entrena la configuración elegida y la evalúa una sola vez en los 2000 registros de prueba."""
    if evaluar is not True:
        p.nota("Todavía no se evaluó nada en prueba. Cuando haya elegido su configuración, cambie EVALUAR_EN_PRUEBA a True "
               "y ejecute la celda.", "info", "La prueba espera su decisión")
        return None
    torch = _torch()
    capas, dropout, tasa = _validar_capas(capas, "CAPAS_FINAL"), _validar_dropout(dropout), _validar_tasa(tasa)
    epocas = _validar_entero(epocas, "EPOCAS_FINAL", 1, 1000, 100)
    paciencia = _validar_paciencia(paciencia, "PACIENCIA_FINAL")
    r = _entrenar(datos, capas, dropout, tasa, epocas, len(datos.entrenamiento), paciencia, nombre="configuración final")
    config = r.config
    if config not in _EVALUADAS_EN_PRUEBA:
        _EVALUADAS_EN_PRUEBA.append(config)
    x_p, _ = _tensores(datos, datos.prueba, r.media, r.desviacion, torch)
    with torch.no_grad():
        prediccion = (r.red(x_p) > 0).numpy().ravel()
    real = datos.y[datos.prueba] == 1
    final = copy.copy(r)
    final.nombre = "configuración final, en prueba"
    final.vp, final.fn = int((prediccion & real).sum()), int((~prediccion & real).sum())
    final.fp, final.vn = int((prediccion & ~real).sum()), int((~prediccion & ~real).sum())
    _anotar(final, "prueba")
    base = 1 - datos.fallas(datos.prueba) / len(datos.prueba)
    p.mostrar_tabla([{"parte": "validación (3000)", "exactitud": _pct(r.exactitud, 2), "fallas detectadas": f"{r.vp} de {r.vp + r.fn}",
                      "falsas alarmas": r.fp},
                     {"parte": "prueba (2000)", "exactitud": _pct(final.exactitud, 2),
                      "fallas detectadas": f"{final.vp} de {final.vp + final.fn}", "falsas alarmas": final.fp}],
                    titulo=f"La configuración final · {list(capas)}, dropout {dropout:g}, tasa {_tasa_texto(tasa)}, "
                           f"{epocas} épocas" + (f", paciencia {paciencia}" if paciencia else ""))
    graficas.matriz_fallas(final.vp, final.fn, final.fp, final.vn, "Matriz de confusión en prueba")
    p.nota(f"En prueba, responder siempre «no falla» acertaría el {_pct(base, 2)}.", "info")
    if len(_EVALUADAS_EN_PRUEBA) > 1:
        p.nota(f"Ya evaluó {len(_EVALUADAS_EN_PRUEBA)} configuraciones en prueba en esta sesión. Si eligió entre ellas "
               "mirando la prueba, su resultado ya no es una estimación honesta: la prueba se volvió otra validación.",
               "aviso", "La prueba se mira una sola vez")
    return final
