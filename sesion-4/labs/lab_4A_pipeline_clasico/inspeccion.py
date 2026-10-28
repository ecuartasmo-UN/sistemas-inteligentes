"""Pipeline clásico de inspección visual para el Laboratorio 4A (Sesión 4 de Sistemas Inteligentes).

Contiene las etapas del pipeline (canal, suavizado, umbral, morfología, regiones y separación),
la comparación con un conteo de referencia, la lámpara simulada, la medición de forma, el patrón
de calibración para estudiar la perspectiva y la bitácora de configuraciones. Los mensajes de error
explican en español qué revisar.
"""
from __future__ import annotations

import csv
import json
import unicodedata
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage as ndi
from skimage.feature import peak_local_max
from skimage.measure import label, regionprops
from skimage.segmentation import watershed

import presentacion as p

CARPETA_IMAGENES = Path("imagenes")
REFERENCIAS = CARPETA_IMAGENES / "referencias.json"
LADO_MAXIMO = 1000          # las fotos más grandes se reducen a este tamaño para que todo corra rápido
CANALES = ("gris", "saturacion", "rojo", "verde", "azul")
PARAMETROS_INICIALES = {"canal": "gris", "suavizado": 5, "umbral": "otsu", "apertura": 0, "cierre": 0,
                        "rellenar": False, "area_minima": 0, "separar": False, "distancia_minima": 30}
_OPCIONALES = {"objetos": "auto"}


class ErrorDeLaboratorio(Exception):
    """Un problema de configuración que la pareja puede corregir: se muestra en una caja roja, sin traza."""


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
    """Minúsculas, sin tildes ni espacios sobrantes: «Saturación » → «saturacion»."""
    t = unicodedata.normalize("NFD", str(texto).strip().lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


# ------------------------------------------------------------------ imágenes y referencias

def ruta_imagen(nombre) -> Path:
    """Busca la imagen tal como se escribió o dentro de la carpeta imagenes/."""
    ruta = Path(nombre)
    if ruta.exists():
        return ruta
    if (CARPETA_IMAGENES / ruta).exists():
        return CARPETA_IMAGENES / ruta
    raise ErrorDeLaboratorio(
        f"No encuentro la imagen «{nombre}». Revise el nombre (con su extensión, por ejemplo .jpg) y la carpeta: "
        "las del laboratorio están en imagenes/ y las suyas deben ir en mis_fotos/.")


def cargar(nombre, lado_maximo: int | None = LADO_MAXIMO) -> np.ndarray:
    """Lee una imagen en color (BGR, como la usa OpenCV), la endereza según el celular y la reduce si es grande."""
    ruta = ruta_imagen(nombre)
    try:
        foto = ImageOps.exif_transpose(Image.open(ruta)).convert("RGB")
    except OSError:
        raise ErrorDeLaboratorio(f"No pude abrir «{ruta}» como imagen. Use una foto .jpg o .png.") from None
    escala = lado_maximo / max(foto.size) if lado_maximo else 1
    if escala < 1:
        foto = foto.resize((round(foto.width * escala), round(foto.height * escala)), Image.LANCZOS)
    return cv2.cvtColor(np.asarray(foto), cv2.COLOR_RGB2BGR)


def referencia(nombre) -> dict | None:
    """El conteo de referencia de una imagen del laboratorio: cantidad y centro de cada cápsula. None si no hay."""
    if not REFERENCIAS.exists():
        return None
    return json.loads(REFERENCIAS.read_text(encoding="utf-8")).get(Path(nombre).name)


def simular_lampara(imagen: np.ndarray, intensidad: int = 140) -> np.ndarray:
    """Suma luz blanca que entra por la izquierda y se desvanece hacia la derecha, como una lámpara a un lado."""
    rampa = np.linspace(intensidad, 0, imagen.shape[1])[None, :, None]
    return np.clip(imagen.astype(float) + rampa, 0, 255).astype(np.uint8)


# ------------------------------------------------------------------ parámetros

def validar(parametros: dict) -> tuple[dict, list[str]]:
    """Revisa los parámetros, completa los que falten con los iniciales y devuelve (parámetros, avisos)."""
    if not isinstance(parametros, dict):
        raise ErrorDeLaboratorio("PARAMETROS debe ser un diccionario: {\"canal\": \"gris\", \"suavizado\": 5, ...}.")
    validos = set(PARAMETROS_INICIALES) | set(_OPCIONALES)
    desconocidos = [k for k in parametros if k not in validos]
    if desconocidos:
        raise ErrorDeLaboratorio(f"No reconozco {', '.join(repr(k) for k in desconocidos)}. "
                                 f"Los parámetros válidos son: {', '.join(PARAMETROS_INICIALES)}.")
    q = {**PARAMETROS_INICIALES, **_OPCIONALES, **parametros}
    avisos = []

    q["canal"] = _normal(q["canal"])
    if q["canal"] not in CANALES:
        raise ErrorDeLaboratorio(f"El canal «{parametros.get('canal')}» no existe. Use uno de estos: {', '.join(CANALES)}.")

    for clave in ("suavizado", "apertura", "cierre", "area_minima", "distancia_minima"):
        valor = q[clave]
        if isinstance(valor, str) and valor.strip().isdigit():
            raise ErrorDeLaboratorio(f"«{clave}» debe ser un número sin comillas: escriba {valor.strip()} en lugar de {valor!r}.")
        if isinstance(valor, bool) or not isinstance(valor, (int, float)) or valor < 0:
            raise ErrorDeLaboratorio(f"«{clave}» debe ser un número entero mayor o igual que 0; recibí {valor!r}.")
        q[clave] = int(round(valor))
    if q["suavizado"] > 1 and q["suavizado"] % 2 == 0:
        q["suavizado"] += 1
        avisos.append(f"El suavizado necesita un tamaño impar: usé {q['suavizado']}.")
    for clave in ("suavizado", "apertura", "cierre"):
        if q[clave] > 51:
            avisos.append(f"«{clave}» = {q[clave]} es muy grande para una imagen de {LADO_MAXIMO} píxeles: pruebe valores entre 3 y 15.")
    if q["distancia_minima"] < 5:
        q["distancia_minima"] = 5
        avisos.append("La distancia mínima entre centros se subió a 5 píxeles.")

    u = q["umbral"]
    if isinstance(u, str):
        if u.strip().isdigit():
            raise ErrorDeLaboratorio(f"Un umbral fijo se escribe sin comillas: {u.strip()} en lugar de {u!r}.")
        u = _normal(u)
        if u not in ("otsu", "adaptativo"):
            raise ErrorDeLaboratorio(f"El umbral «{q['umbral']}» no es válido: use \"otsu\", \"adaptativo\" o un número de 0 a 255.")
        q["umbral"] = u
    elif isinstance(u, bool) or not isinstance(u, (int, float)) or not 0 <= u <= 255:
        raise ErrorDeLaboratorio(f"El umbral debe ser \"otsu\", \"adaptativo\" o un número de 0 a 255; recibí {u!r}.")
    else:
        q["umbral"] = int(round(u))

    for clave in ("rellenar", "separar"):
        if not isinstance(q[clave], bool):
            raise ErrorDeLaboratorio(f"«{clave}» debe ser True o False (sin comillas); recibí {q[clave]!r}.")
    q["objetos"] = _normal(q["objetos"])
    if q["objetos"] not in ("auto", "claros", "oscuros"):
        raise ErrorDeLaboratorio("«objetos» debe ser \"auto\", \"claros\" u \"oscuros\".")
    return q, avisos


# ------------------------------------------------------------------ el pipeline

@dataclass
class Region:
    id: int
    x: float            # centro, en píxeles
    y: float
    area: int           # en píxeles
    largo: float        # eje mayor de la elipse equivalente, en píxeles
    ancho: float        # eje menor
    caja: tuple         # (fila mínima, columna mínima, fila máxima, columna máxima)


@dataclass
class Resultado:
    nombre: str
    imagen: np.ndarray
    parametros: dict
    etapas: list = field(default_factory=list)       # (título, imagen) de cada etapa
    canal: np.ndarray | None = None
    umbral: float | None = None                       # el umbral que se usó de verdad (Otsu lo calcula)
    mascara: np.ndarray | None = None
    etiquetas: np.ndarray | None = None
    regiones: list = field(default_factory=list)
    descartadas: int = 0                              # regiones más pequeñas que el área mínima
    distancia: np.ndarray | None = None               # solo si se separaron objetos
    marcas: np.ndarray | None = None
    avisos: list = field(default_factory=list)

    @property
    def conteo(self) -> int:
        return len(self.regiones)

    def __repr__(self) -> str:   # una línea, en lugar de todas las tablas de números
        return f"Resultado({self.nombre}: {self.conteo} regiones)"


def extraer_canal(imagen: np.ndarray, canal: str) -> np.ndarray:
    """Una sola tabla de números (0 a 255) a partir de la imagen en color."""
    if canal == "gris":
        return cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    if canal == "saturacion":
        return cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)[:, :, 1]
    return imagen[:, :, {"azul": 0, "verde": 1, "rojo": 2}[canal]].copy()


def _elipse(lado: int) -> np.ndarray:
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (lado, lado))


def procesar(imagen: np.ndarray, parametros: dict, nombre: str = "imagen") -> Resultado:
    """Corre el pipeline completo y guarda la imagen de cada etapa."""
    q, avisos = validar(parametros)
    r = Resultado(nombre=nombre, imagen=imagen, parametros=q, avisos=avisos)
    r.etapas.append(("1 · Original", cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)))

    canal = extraer_canal(imagen, q["canal"])
    r.etapas.append((f"2 · Canal: {q['canal']}", canal))

    k = q["suavizado"]
    suave = cv2.GaussianBlur(canal, (k, k), 0) if k > 1 else canal
    r.canal = suave
    r.etapas.append((f"3 · Suavizado {k}×{k}" if k > 1 else "3 · Sin suavizado", suave))

    if q["umbral"] == "otsu":
        r.umbral, binaria = cv2.threshold(suave, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        titulo = f"4 · Umbral de Otsu: {r.umbral:.0f}"
    elif q["umbral"] == "adaptativo":
        binaria = cv2.adaptiveThreshold(suave, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 151, -5)
        titulo = "4 · Umbral adaptativo"
    else:
        r.umbral, binaria = cv2.threshold(suave, q["umbral"], 255, cv2.THRESH_BINARY)
        titulo = f"4 · Umbral fijo: {q['umbral']}"
    # ¿Los objetos son lo claro o lo oscuro? En «auto», el fondo es lo que más aparece en el borde de la foto
    invertir = q["objetos"] == "oscuros" or (
        q["objetos"] == "auto" and np.concatenate([binaria[0], binaria[-1], binaria[:, 0], binaria[:, -1]]).mean() > 127)
    if invertir:
        binaria = 255 - binaria
    r.etapas.append((titulo, binaria))

    limpia = binaria
    if q["apertura"] > 1:
        limpia = cv2.morphologyEx(limpia, cv2.MORPH_OPEN, _elipse(q["apertura"]))
    if q["cierre"] > 1:
        limpia = cv2.morphologyEx(limpia, cv2.MORPH_CLOSE, _elipse(q["cierre"]))
    if q["rellenar"]:
        limpia = (ndi.binary_fill_holes(limpia > 0) * 255).astype(np.uint8)
    pasos = [n for n, v in (("apertura", q["apertura"] > 1), ("cierre", q["cierre"] > 1), ("rellenar", q["rellenar"])) if v]
    r.etapas.append(("5 · Morfología: " + (", ".join(pasos) if pasos else "ninguna"), limpia))
    r.mascara = limpia > 0

    if q["separar"]:
        etiquetas = _separar(r, q["distancia_minima"])
    else:
        etiquetas = label(r.mascara)

    # Área mínima: las regiones más pequeñas se descartan como ruido
    regiones = []
    for reg in regionprops(etiquetas):
        if reg.area < q["area_minima"]:
            etiquetas[etiquetas == reg.label] = 0
            r.descartadas += 1
        else:
            regiones.append(reg)
    # Numeración en orden de lectura: por franjas de arriba abajo y, en cada franja, de izquierda a derecha
    regiones.sort(key=lambda g: (round(g.centroid[0] / 110), g.centroid[1]))
    final = np.zeros_like(etiquetas)
    for i, reg in enumerate(regiones, 1):
        final[etiquetas == reg.label] = i
        r.regiones.append(Region(i, float(reg.centroid[1]), float(reg.centroid[0]), int(reg.area),
                                 float(reg.axis_major_length), float(reg.axis_minor_length), tuple(reg.bbox)))
    r.etiquetas = final
    titulo = f"6 · Regiones: {r.conteo}"
    if r.descartadas:
        titulo += f" (y {r.descartadas} descartadas por pequeñas)"
    r.etapas.append((titulo, final))
    return r


def _separar(r: Resultado, distancia_minima: int) -> np.ndarray:
    """Separa objetos que se tocan: transformada de distancia, un centro por objeto y crecimiento de regiones."""
    mascara = r.mascara.astype(np.uint8)
    distancia = cv2.distanceTransform(mascara, cv2.DIST_L2, 5)
    suave = cv2.GaussianBlur(distancia, (0, 0), 2)
    componentes = label(r.mascara)
    picos = peak_local_max(suave, min_distance=distancia_minima, threshold_abs=0.4 * float(distancia.max()),
                           labels=componentes, exclude_border=False)
    marcas = np.zeros(distancia.shape, int)
    for i, (fila, col) in enumerate(picos, 1):
        marcas[fila, col] = i
    # Cada mancha necesita al menos un centro: las pequeñas, sin pico, reciben uno en su punto más interior
    siguiente = len(picos) + 1
    for comp in regionprops(componentes):
        filas, cols = comp.coords[:, 0], comp.coords[:, 1]
        if not marcas[filas, cols].any():
            j = int(np.argmax(distancia[filas, cols]))
            marcas[filas[j], cols[j]] = siguiente
            siguiente += 1
    r.distancia, r.marcas = distancia, marcas
    return watershed(-distancia, marcas, mask=r.mascara)


# ------------------------------------------------------------------ comparar con la referencia

@dataclass
class Comparacion:
    cantidad: int                                   # cápsulas en la referencia
    correctas: list = field(default_factory=list)   # regiones con exactamente una cápsula
    fusionadas: dict = field(default_factory=dict)  # región → cuántas cápsulas contiene
    sobrantes: list = field(default_factory=list)   # regiones sin ninguna cápsula: fragmentos, reflejos o ruido
    perdidas: list = field(default_factory=list)    # centros de cápsulas que ninguna región cubre

    @property
    def exacta(self) -> bool:
        return not (self.fusionadas or self.sobrantes or self.perdidas) and len(self.correctas) == self.cantidad


def comparar(r: Resultado, ref: dict) -> Comparacion:
    """Cruza las regiones con los centros de referencia: cuáles aciertan, cuáles juntan dos y cuáles sobran."""
    c = Comparacion(cantidad=ref["cantidad"])
    contenidos = {g.id: 0 for g in r.regiones}
    alto, ancho = r.etiquetas.shape
    for x, y in ref["centros"]:
        x, y = int(round(x)), int(round(y))
        etiqueta = int(r.etiquetas[y, x])
        if etiqueta == 0:   # el centro cayó en un hueco: se busca la región más cercana a pocos píxeles
            ventana = r.etiquetas[max(0, y - 6):min(alto, y + 7), max(0, x - 6):min(ancho, x + 7)]
            valores = ventana[ventana > 0]
            etiqueta = int(np.bincount(valores).argmax()) if valores.size else 0
        if etiqueta == 0:
            c.perdidas.append((x, y))
        else:
            contenidos[etiqueta] += 1
    for i, n in contenidos.items():
        if n == 0:
            c.sobrantes.append(i)
        elif n == 1:
            c.correctas.append(i)
        else:
            c.fusionadas[i] = n
    return c


# ------------------------------------------------------------------ bitácora

ARCHIVO_BITACORA = Path("resultados_4A.csv")
BITACORA: list[dict] = []   # las corridas de esta sesión del kernel; el archivo guarda todas


def _leer_bitacora() -> list[dict]:
    if not ARCHIVO_BITACORA.exists():
        return []
    with open(ARCHIVO_BITACORA, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


COLUMNAS = ["n", "hora", "seccion", "imagen", "canal", "suavizado", "umbral", "umbral_usado", "apertura", "cierre",
            "rellenar", "area_minima", "separar", "distancia_minima", "regiones", "correctas", "fusionadas", "de_mas",
            "perdidas", "referencia", "conteo_a_mano", "detalle"]


def _escribir(fila: dict) -> None:
    """Agrega una fila a resultados_4A.csv en el momento: reiniciar el kernel no borra la bitácora."""
    fila = {**{k: "" for k in COLUMNAS}, **fila, "n": len(_leer_bitacora()) + 1,
            "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    BITACORA.append(fila)
    nuevo = not ARCHIVO_BITACORA.exists()
    with open(ARCHIVO_BITACORA, "a", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=COLUMNAS)
        if nuevo:
            escritor.writeheader()
        escritor.writerow({k: ("" if fila[k] is None else fila[k]) for k in COLUMNAS})


def registrar(r: Resultado, comp: Comparacion | None, seccion: str, imagen: str, conteo_a_mano=None,
              detalle: str = "") -> None:
    """Agrega a la bitácora los parámetros y el resultado de una corrida."""
    q = r.parametros
    _escribir({
        "seccion": seccion, "imagen": imagen, "canal": q["canal"], "suavizado": q["suavizado"],
        "umbral": q["umbral"], "umbral_usado": None if r.umbral is None else round(float(r.umbral)),
        "apertura": q["apertura"], "cierre": q["cierre"], "rellenar": q["rellenar"], "area_minima": q["area_minima"],
        "separar": q["separar"], "distancia_minima": q["distancia_minima"], "regiones": r.conteo,
        "correctas": None if comp is None else len(comp.correctas),
        "fusionadas": None if comp is None else len(comp.fusionadas),
        "de_mas": None if comp is None else len(comp.sobrantes),
        "perdidas": None if comp is None else len(comp.perdidas),
        "referencia": None if comp is None else comp.cantidad, "conteo_a_mano": conteo_a_mano, "detalle": detalle,
    })


def mostrar_bitacora(ultimas: int | None = None, seccion: str | None = None) -> None:
    """Muestra la bitácora de resultados_4A.csv: todas las filas, las de una sección o las últimas."""
    filas = _leer_bitacora()
    if seccion is not None:
        filas = [f for f in filas if f["seccion"] == str(seccion)]
    if not filas:
        p.nota("La bitácora no tiene corridas" + (f" de la sección {seccion}" if seccion else "") + " todavía.", "aviso")
        return
    filas = filas[-ultimas:] if ultimas else filas
    columnas = ["n", "seccion", "imagen", "canal", "umbral", "apertura", "rellenar", "area_minima", "separar",
                "distancia_minima", "regiones", "correctas", "fusionadas", "de_mas", "perdidas", "detalle"]
    if seccion is not None:   # en la vista de una sección sobran la sección y la imagen
        columnas = [c for c in columnas if c not in ("seccion", "canal")]
    titulo = "Bitácora de configuraciones" + (f": sección {seccion}" if seccion else "")
    p.mostrar_tabla([{k: f.get(k, "") for k in columnas} for f in filas], titulo=titulo)


def revisar_bitacora() -> None:
    """Confirma cuántas corridas tiene resultados_4A.csv, el archivo que se entrega."""
    filas = _leer_bitacora()
    if not filas:
        p.nota("Todavía no hay corridas en resultados_4A.csv.", "aviso")
        return
    secciones = list(dict.fromkeys(f["seccion"] for f in filas))   # en el orden en que aparecen
    p.nota(f"resultados_4A.csv tiene {len(filas)} corridas, de las secciones {', '.join(secciones)}. "
           "Se guardó una por una: reiniciar el kernel no la borra. Es el archivo que se entrega.", "exito")


# ------------------------------------------------------------------ una corrida completa, con su informe

def _consejos(comp: Comparacion, q: dict) -> list[str]:
    """Qué revisar, según lo que falla y según si la separación está activa."""
    consejos = []
    if comp.fusionadas:
        if q["separar"] and q["umbral"] != "otsu":
            consejos.append("Con la separación activa ya no hace falta un umbral alto: pruebe primero \"otsu\" en "
                            "UMBRAL_SECCION_7 (sección 7), sin cambiar la distancia mínima.")
        elif q["separar"]:
            consejos.append("Con la separación activa, una región que junta dos cápsulas pide una distancia mínima menor.")
        else:
            consejos.append("Hay regiones que juntan dos cápsulas: algo las une. Subir el umbral corta el halo (sección 6); "
                            "las que se tocan de verdad se separan en la sección 7.")
    if comp.sobrantes:
        if q["separar"]:
            consejos.append("Con la separación activa, las regiones de más suelen ser cápsulas partidas en dos: "
                            "suba la distancia mínima.")
        else:
            consejos.append("Hay regiones sin cápsula: fragmentos, reflejos o textura de la tela. Una apertura más grande "
                            "o un área mínima las quitan; un umbral demasiado alto también parte cápsulas.")
    if comp.perdidas:
        consejos.append("Hay cápsulas que ninguna región cubre: el umbral las dejó por fuera, o el área mínima borró el "
                        "trozo donde estaba su centro.")
    return consejos


@_amable
def inspeccionar(nombre, parametros: dict, seccion: str = "", lampara: int = 0, etapas: bool = True,
                 conteo_a_mano=None, con_referencia: bool = True) -> Resultado | None:
    """Corre el pipeline sobre una imagen, lo compara con la referencia (si la hay) y lo anota en la bitácora."""
    import vista
    if isinstance(lampara, bool) or not isinstance(lampara, (int, float)) or lampara < 0:
        raise ErrorDeLaboratorio(f"La intensidad de la lámpara debe ser un número de 0 a 400; recibí {lampara!r}.")
    imagen = cargar(nombre)
    if lampara:
        imagen = simular_lampara(imagen, int(lampara))
    etiqueta = Path(nombre).name + (f" + lámpara {lampara}" if lampara else "")
    r = procesar(imagen, parametros, etiqueta)
    for aviso in r.avisos:
        p.nota(aviso, "aviso")
    ref = referencia(nombre) if con_referencia else None
    comp = comparar(r, ref) if ref else None
    registrar(r, comp, seccion, etiqueta, conteo_a_mano)
    if etapas:
        vista.mostrar_etapas(r)
    vista.mostrar_comparacion(r, comp)
    _informe(r, comp, conteo_a_mano, seccion)
    return r


@_amable
def validar_configuracion(parametros: dict, lampara: int = 140) -> bool | None:
    """Prueba una configuración en las tres fotos con referencia y con la lámpara, sin figuras: una fila por prueba."""
    pruebas = [("capsulas_principal.jpg", 0), ("capsulas_juntas.jpg", 0), ("capsulas_deforme.jpg", 0),
               ("capsulas_principal.jpg", lampara)]
    filas, todas = [], True
    for nombre, lamp in pruebas:
        imagen = cargar(nombre)
        if lamp:
            imagen = simular_lampara(imagen, lamp)
        r = procesar(imagen, parametros, nombre)
        comp = comparar(r, referencia(nombre))
        todas &= comp.exacta
        filas.append({"foto": nombre + (f" + lámpara {lamp}" if lamp else ""), "regiones": r.conteo,
                      "correctas": len(comp.correctas), "juntan dos": len(comp.fusionadas), "de más": len(comp.sobrantes),
                      "perdidas": len(comp.perdidas), "resultado": "✓" if comp.exacta else "✗"})
    p.mostrar_tabla(filas, titulo="Su configuración en las tres fotos y con la lámpara")
    if todas:
        p.nota("✓ La configuración cuenta bien las tres fotos y resiste la lámpara. Es la que se entrega.", "exito")
        return True
    sin_lampara = all(f["resultado"] == "✓" for f in filas[:3])
    if sin_lampara:
        p.nota("Las tres fotos están bien, pero la lámpara la rompe. Mire el umbral: en la celda ✏️ de la sección 7, "
               "escriba UMBRAL_SECCION_7 = \"otsu\" y ejecute otra vez, en orden, las celdas de las secciones 7 y 8.", "aviso")
    else:
        p.nota("Hay fotos en ✗ aun sin lámpara. Revise la separación y el umbral en la celda ✏️ de la sección 7 y "
               "ejecute otra vez, en orden, las celdas de las secciones 7 y 8.", "aviso")
    return False


def _informe(r: Resultado, comp: Comparacion | None, conteo_a_mano=None, seccion: str = "") -> None:
    rotulo = f"Corrida {len(_leer_bitacora())}" + (f" · sección {seccion}" if seccion else "") + f" · {r.nombre}"
    if comp is None:
        texto = f"El pipeline encontró <b>{r.conteo}</b> regiones."
        if isinstance(conteo_a_mano, int):
            dif = r.conteo - conteo_a_mano
            texto += f" Su conteo a mano: <b>{conteo_a_mano}</b> (diferencia {dif:+d})."
        p.caja(texto, "info", rotulo)
        return
    if comp.exacta:
        p.caja(f"✓ Las {comp.cantidad} cápsulas, cada una en su propia región, y ninguna región de más.",
               "exito", f"{rotulo}: {r.conteo} regiones")
        return
    if seccion == "6" and len(comp.fusionadas) <= 1 and not comp.sobrantes and not comp.perdidas:
        p.caja(f"✓ Meta de la sección 6 cumplida: {len(comp.correctas)} cápsulas en su propia región y un solo par "
               "unido, que se toca de verdad. Ese par se separa en la sección 7.", "exito", f"{rotulo}: {r.conteo} regiones")
        return
    partes = [f"Regiones: <b>{r.conteo}</b> · cápsulas en la referencia: <b>{comp.cantidad}</b>",
              f"✓ Correctas (una cápsula cada una): <b>{len(comp.correctas)}</b>"]
    if comp.fusionadas:
        partes.append("✗ Juntan dos o más cápsulas: regiones " + ", ".join(f"<b>{i}</b> ({n})" for i, n in comp.fusionadas.items()))
    if comp.sobrantes:
        partes.append("✗ Sin cápsula (de más): regiones " + ", ".join(f"<b>{i}</b>" for i in comp.sobrantes[:20])
                      + (" …" if len(comp.sobrantes) > 20 else ""))
    if comp.perdidas:
        partes.append(f"✗ Cápsulas perdidas: <b>{len(comp.perdidas)}</b> (marcadas con una X magenta)")
    consejos = "".join(f"<li>{c}</li>" for c in _consejos(comp, r.parametros))
    p.caja("<br>".join(partes) + (f"<ul style='margin:6px 0 0 18px'>{consejos}</ul>" if consejos else ""),
           "aviso", f"{rotulo}: todavía no coincide")


# ------------------------------------------------------------------ comprobaciones de los ejercicios

def comprobar_canal(canal, imagen: np.ndarray | None = None) -> None:
    """Orienta la elección del canal de la sección 4; con la imagen, muestra el histograma de un canal distinto."""
    try:
        c = _normal(canal)
    except Exception:
        c = ""
    if c in ("", "none") or canal is None:
        p.nota("Escriba un canal en CANAL, por ejemplo \"saturacion\".", "aviso")
    elif c not in CANALES:
        p.nota(f"«{canal}» no es un canal. Use uno de estos: {', '.join(CANALES)}.", "error")
    elif c == "saturacion":
        p.nota("Buena elección: en la saturación, el fondo gris queda cerca de 0 y las cápsulas verdes, muy arriba. "
               "El histograma tiene dos montañas y el umbral cae entre ellas.", "exito")
    elif c == "gris":
        p.nota("Con el gris, las dos montañas del histograma se tocan: la tela en sombra tiene el mismo brillo que las "
               "cápsulas y queda del lado equivocado del umbral. Mire otra vez los dos histogramas.", "aviso")
    else:
        p.nota(f"Puede probar «{c}», pero compare su histograma con el de la saturación: ¿cuál separa mejor el fondo "
               "de las cápsulas?", "info")
        if imagen is not None:
            import vista
            vista.mostrar_histogramas(imagen, ["saturacion", c])


def comprobar_conteo(conteo, nombre) -> None:
    """Compara el conteo a mano con la referencia del laboratorio."""
    ref = referencia(nombre)
    if conteo is None:
        p.nota("Escriba su conteo en CONTEO_A_MANO (un número entero) y ejecute de nuevo.", "aviso")
        return
    if isinstance(conteo, bool) or not isinstance(conteo, int) or conteo < 0:
        p.nota(f"CONTEO_A_MANO debe ser un número entero, sin comillas; recibí {conteo!r}.", "error")
        return
    if ref is None:
        p.nota(f"Su conteo: {conteo}. Esta imagen no tiene referencia; su conteo es la referencia.", "info")
    elif conteo == ref["cantidad"]:
        p.nota(f"✓ Su conteo coincide con la referencia del laboratorio: {conteo} cápsulas.", "exito")
    else:
        p.nota(f"Su conteo ({conteo}) no coincide con la referencia del laboratorio ({ref['cantidad']}). "
               "Cuente de nuevo por casillas de la cuadrícula: es fácil saltarse una cápsula en el borde de una casilla.", "aviso")


# ------------------------------------------------------------------ medir y decidir

def medir(r: Resultado) -> list[dict]:
    """Largo, ancho, área y alargamiento (largo ÷ ancho) de cada región, y su diferencia con la cápsula típica (la mediana)."""
    if not r.regiones:
        return []
    alargamientos = [g.largo / max(g.ancho, 1.0) for g in r.regiones]   # una región de un píxel tiene ancho 0
    med_alarg = float(np.median(alargamientos))
    med_area = float(np.median([g.area for g in r.regiones]))
    filas = []
    for g, alarg in zip(r.regiones, alargamientos):
        filas.append({"region": g.id, "largo_px": round(g.largo), "ancho_px": round(g.ancho), "area_px": g.area,
                      "alargamiento": alarg, "dif_alargamiento": alarg / med_alarg - 1, "dif_area": g.area / med_area - 1})
    return filas


@_amable
def revisar_forma(nombre, parametros: dict, tolerancia, seccion: str = "9") -> list | None:
    """Marca las cápsulas cuyo alargamiento (largo ÷ ancho) se aleja del típico más que la tolerancia (en %)."""
    import vista
    if isinstance(tolerancia, bool) or not isinstance(tolerancia, (int, float)) or not 0 < tolerancia < 100:
        raise ErrorDeLaboratorio(f"TOLERANCIA debe ser un porcentaje entre 0 y 100, por ejemplo 20; recibí {tolerancia!r}.")
    r = procesar(cargar(nombre), parametros, Path(nombre).name)
    filas = medir(r)
    fuera = [f["region"] for f in filas if abs(f["dif_alargamiento"]) > tolerancia / 100]
    ref = referencia(nombre)
    comp = comparar(r, ref) if ref else None
    registrar(r, comp, seccion, Path(nombre).name,
              detalle=f"tolerancia {tolerancia:g} %; rechazadas: {', '.join(map(str, fuera)) or 'ninguna'}")
    vista.mostrar_forma(r, fuera, tolerancia)
    tipica = float(np.median([f["alargamiento"] for f in filas])) if filas else 0
    # Las cinco más alejadas en alargamiento y las dos más alejadas en área, sin repetir
    por_alarg = sorted(filas, key=lambda f: -abs(f["dif_alargamiento"]))[:5]
    por_area = [f for f in sorted(filas, key=lambda f: -abs(f["dif_area"])) if f not in por_alarg][:2]
    tabla = [{"región": f["region"], "largo (px)": f["largo_px"], "ancho (px)": f["ancho_px"],
              "alargamiento": f"{f['alargamiento']:.2f}", "alargamiento vs. típica": f"{f['dif_alargamiento']:+.1%}",
              "área vs. típica": f"{f['dif_area']:+.0%}", "decisión": "rechazar" if f["region"] in fuera else "pasa"}
             for f in por_alarg + por_area]
    p.mostrar_tabla(tabla, titulo=f"Las cápsulas más alejadas de la típica, en alargamiento o en área "
                                  f"(alargamiento típico: {tipica:.2f})")
    # Comprobación: ¿se marcó la cápsula deforme, y solo ella?
    if ref and ref.get("deforme"):
        x, y = ref["deforme"]
        objetivo = int(r.etiquetas[int(y), int(x)])
        if comp and not comp.exacta:
            p.nota("Antes de medir, el conteo debe ser correcto: la medición hereda los errores de la segmentación. "
                   "Use la configuración que dejó todo bien en la sección 7.", "aviso")
        elif fuera == [objetivo]:
            p.nota(f"✓ Solo la región {objetivo} queda fuera de la tolerancia: es la cápsula deforme.", "exito")
        elif objetivo in fuera:
            p.nota(f"La región {objetivo} (la deforme) está marcada, pero también {len(fuera) - 1} cápsula(s) normal(es): "
                   "la tolerancia es muy estrecha y rechazaría producto bueno.", "aviso")
        else:
            p.nota("La cápsula deforme pasa la inspección: la tolerancia es muy amplia. Pruebe un porcentaje menor.", "aviso")
    return fuera


# ------------------------------------------------------------------ el patrón de calibración y la perspectiva

def cuadros_del_patron(nombre="patron_calibracion.jpg") -> list[dict]:
    """Encuentra los cuadros negros del patrón, como en el ejemplo de la charla: gris, Otsu, apertura y filtros de forma."""
    color = cargar(nombre, lado_maximo=None)   # a su tamaño original, para que coincida con la charla
    gris = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)
    suave = cv2.GaussianBlur(gris, (5, 5), 0)
    _, binaria = cv2.threshold(suave, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    limpia = cv2.morphologyEx(binaria, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7)))
    n, _, stats, centros = cv2.connectedComponentsWithStats(limpia)
    cuadros = []
    for i in range(1, n):
        x, y, w, h, area = (int(v) for v in stats[i])
        if area < 800 or not 0.6 < w / h < 1.6 or area / (w * h) < 0.7:
            continue   # ruido y regiones que no parecen cuadros
        cuadros.append({"x": x, "y": y, "w": w, "h": h, "area": area, "lado_px": float(np.sqrt(area)),
                        "cx": float(centros[i][0]), "cy": float(centros[i][1])})
    return cuadros


@_amable
def perspectiva(lado_mm, nombre="patron_calibracion.jpg") -> dict | None:
    """Convierte el lado de cada cuadro a milímetros con un solo factor y muestra cuánto cambia por la perspectiva."""
    import vista
    if lado_mm is None:
        raise ErrorDeLaboratorio("Escriba en LADO_MM el lado real de los cuadros, en milímetros: 50.")
    if isinstance(lado_mm, bool) or not isinstance(lado_mm, (int, float)) or lado_mm <= 0:
        raise ErrorDeLaboratorio(f"LADO_MM debe ser un número positivo de milímetros; recibí {lado_mm!r}.")
    todos = cuadros_del_patron(nombre)
    ref = referencia(nombre) or {}
    # Las dos franjas de la base no son cuadros del patrón: la referencia indica dónde empiezan
    limite = ref.get("base_desde_y")
    cuadros = [c for c in todos if limite is None or c["cy"] < limite]
    lados = np.array([c["lado_px"] for c in cuadros])
    factor = lado_mm / float(np.median(lados))          # milímetros por píxel, con el cuadro típico
    medidos = lados * factor
    base = [c for c in todos if c not in cuadros]
    vista.mostrar_patron(cargar(nombre, lado_maximo=None), cuadros, factor, base)
    _escribir({"seccion": "9.2", "imagen": Path(nombre).name, "regiones": len(todos),
               "detalle": f"lado real {lado_mm:g} mm; con un solo factor, de {lados.min() * factor:.1f} "
                          f"a {lados.max() * factor:.1f} mm"})
    resumen = {"cuadros": len(cuadros), "regiones_con_la_base": len(todos), "lado_min_px": float(lados.min()),
               "lado_max_px": float(lados.max()), "mm_por_px": factor, "medido_min_mm": float(medidos.min()),
               "medido_max_mm": float(medidos.max())}
    p.caja(f"El pipeline encontró <b>{len(todos)}</b> regiones: <b>{len(cuadros)}</b> cuadros y {len(todos) - len(cuadros)} "
           f"franjas de la base.<br>El lado de los cuadros va de <b>{lados.min():.0f}</b> a <b>{lados.max():.0f}</b> píxeles, "
           f"aunque todos miden lo mismo.<br>Con un solo factor ({factor:.3f} mm por píxel, el del cuadro típico), "
           f"los cuadros «miden» entre <b>{medidos.min():.1f}</b> y <b>{medidos.max():.1f} mm</b>, aunque todos miden {lado_mm:g} mm.",
           "info", "Un mismo tamaño, muchas medidas")
    return resumen
