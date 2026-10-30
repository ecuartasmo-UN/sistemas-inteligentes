"""Árboles de decisión, reglas, ensambles y validación cruzada del Laboratorio 6A (Sesión 6, Sistemas Inteligentes).

- Lee los pasajeros del Titanic (titanic3, Vanderbilt) o un CSV propio con una columna «conclusion».
- Aplica la regla del experto «mujeres y niños primero».
- Induce árboles de decisión con scikit-learn, los dibuja y los traduce a reglas SI… ENTONCES con sus casos.
- Compara profundidades y ensambles con validación cruzada estratificada, siempre con la semilla 7.
- Responde la pregunta del auditor sobre un pasajero ficticio.
- Anota cada método en el CSV común del contrapunto, resultados_6A.csv: una fila por pasajero y método.
"""
from __future__ import annotations

import csv
import io
import math
import time
import unicodedata
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import numpy as np

import graficas
import presentacion as p

SEMILLA = 7
ARCHIVO_TITANIC = Path("datos") / "titanic3.csv"
CARPETA_CASOS = Path("mis_casos")
ARCHIVO_CSV = "resultados_6A.csv"
SOBREVIVE, NO_SOBREVIVE = "sobrevive", "no sobrevive"
PUERTOS = {"S": "Southampton", "C": "Cherbourg", "Q": "Queenstown"}

_ESTADO: dict = {}          # el último árbol y el último bosque del Titanic, para la pregunta del auditor
_REGISTRO: dict = {}        # filas del CSV común del contrapunto


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


def _normal(texto) -> str:
    """Minúsculas, sin tildes ni espacios sobrantes: «Conclusión » → «conclusion»."""
    t = unicodedata.normalize("NFD", str(texto).strip().lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def _sklearn():
    """Importa scikit-learn, o explica cómo instalarla."""
    try:
        import sklearn  # noqa: F401
    except ImportError:
        raise ErrorDeLaboratorio("No está instalada la librería scikit-learn, que induce los árboles. Ejecute la primera "
                                 "celda del notebook (instala lo que falta) y reinicie el kernel.") from None


# ------------------------------------------------------------------ los datos

@dataclass
class Datos:
    """Un conjunto de casos listo para inducir árboles."""
    nombre: str
    X: np.ndarray                   # una fila por caso; NaN donde falta un valor
    y: np.ndarray                   # la conclusión de cada caso, en texto
    columnas: list                  # cómo se lee cada columna de X en una pregunta o en una regla (diccionarios)
    clases: list                    # las conclusiones posibles, en un orden fijo
    filas: list = field(default_factory=list)   # los casos originales, para mostrarlos y para el LLM
    propio: bool = False
    tarea: str = ""

    @property
    def huella(self) -> str:
        return f"{self.nombre}·{len(self.y)}"

    @property
    def mayoritaria(self) -> str:
        valores, cuentas = np.unique(self.y, return_counts=True)
        return str(valores[np.argmax(cuentas)])


def _columnas_titanic(con_fuga: bool) -> list:
    columnas = [
        {"clave": "clase", "tipo": "ordinal", "nombre": "clase", "etiquetas": {1: "1.ª", 2: "2.ª", 3: "3.ª"}},
        {"clave": "mujer", "tipo": "binaria", "si": "mujer", "no": "hombre", "pregunta": "¿mujer?"},
        {"clave": "edad", "tipo": "real", "nombre": "edad", "unidad": "", "puede_faltar": True, "faltante": "desconocida",
         "conocida": "conocida"},
        {"clave": "hermanos_o_conyuge", "tipo": "entera", "nombre": "hermanos o cónyuge a bordo"},
        {"clave": "padres_o_hijos", "tipo": "entera", "nombre": "padres o hijos a bordo"},
        {"clave": "tarifa", "tipo": "real", "nombre": "tarifa", "unidad": " £", "puede_faltar": True, "faltante": "desconocida",
         "conocida": "conocida"},
        {"clave": "embarco_en_C", "tipo": "binaria", "si": "embarcó en Cherbourg", "no": "no embarcó en Cherbourg",
         "pregunta": "¿embarcó en Cherbourg?"},
        {"clave": "embarco_en_Q", "tipo": "binaria", "si": "embarcó en Queenstown", "no": "no embarcó en Queenstown",
         "pregunta": "¿embarcó en Queenstown?"},
    ]
    if con_fuga:
        columnas += [
            {"clave": "bote", "tipo": "binaria", "si": "subió a un bote", "no": "no subió a un bote",
             "pregunta": "¿subió a un bote salvavidas?"},
            {"clave": "cuerpo", "tipo": "binaria", "si": "su cuerpo se recuperó", "no": "su cuerpo no se recuperó",
             "pregunta": "¿se recuperó su cuerpo?"},
        ]
    return columnas


def _numero_o_nada(texto):
    texto = (texto or "").strip()
    if texto in ("", "NA"):
        return None
    return float(texto)


@_amable
def cargar_titanic(ruta=ARCHIVO_TITANIC, con_fuga: bool = False, mostrar: bool = True) -> Datos | None:
    """Lee los pasajeros del Titanic y muestra algunos, con la línea base de responder siempre «no sobrevive».

    con_fuga=True agrega dos columnas que revelan la respuesta, el bote salvavidas y el cuerpo recuperado (sección 7)."""
    ruta = Path(ruta)
    if not ruta.exists():
        raise ErrorDeLaboratorio(f"No encuentro {ruta}. Abra el notebook desde la carpeta del laboratorio, donde está la "
                                 "carpeta datos/, y reinicie el kernel.")
    with ruta.open(encoding="utf-8") as f:
        crudas = list(csv.DictReader(f))
    filas, X, y = [], [], []
    for c in crudas:
        fila = {"clase": int(c["pclass"]), "sexo": "mujer" if c["sex"] == "female" else "hombre",
                "edad": _numero_o_nada(c["age"]), "hermanos_o_conyuge": int(c["sibsp"]), "padres_o_hijos": int(c["parch"]),
                "tarifa": _numero_o_nada(c["fare"]), "puerto": PUERTOS.get(c["embarked"], ""),
                "bote": c["boat"].strip() not in ("", "NA"), "cuerpo": c["body"].strip() not in ("", "NA")}
        filas.append(fila)
        valores = [fila["clase"], 1.0 if fila["sexo"] == "mujer" else 0.0,
                   np.nan if fila["edad"] is None else fila["edad"], fila["hermanos_o_conyuge"], fila["padres_o_hijos"],
                   np.nan if fila["tarifa"] is None else fila["tarifa"], 1.0 if c["embarked"] == "C" else 0.0,
                   1.0 if c["embarked"] == "Q" else 0.0]
        if con_fuga:
            valores += [1.0 if fila["bote"] else 0.0, 1.0 if fila["cuerpo"] else 0.0]
        X.append(valores)
        y.append(SOBREVIVE if c["survived"] == "1" else NO_SOBREVIVE)
    datos = Datos("Titanic" + (" con bote y cuerpo" if con_fuga else ""), np.array(X, dtype=float), np.array(y),
                  _columnas_titanic(con_fuga), [SOBREVIVE, NO_SOBREVIVE], filas,
                  tarea="Titanic: predecir quién sobrevivió")
    if mostrar:
        _mostrar_titanic(datos)
    return datos


def _mostrar_titanic(datos: Datos) -> None:
    muestra = [0, 1, 4, 13, 140, 337, 600, 1000, 1200]
    tabla = []
    for i in muestra:
        f = datos.filas[i]
        tabla.append({"pasajero": i + 1, "clase": f"{f['clase']}.ª", "sexo": f["sexo"],
                      "edad": "—" if f["edad"] is None else _n(f["edad"], 0 if f["edad"] >= 1 else 2),
                      "hermanos o cónyuge": f["hermanos_o_conyuge"], "padres o hijos": f["padres_o_hijos"],
                      "tarifa (£)": "—" if f["tarifa"] is None else _n(f["tarifa"], 2), "puerto": f["puerto"] or "—",
                      "¿sobrevivió?": "sí" if datos.y[i] == SOBREVIVE else "no"})
    p.mostrar_tabla(tabla, titulo="Algunos pasajeros (— = dato desconocido)")
    n, vivos = len(datos.y), int((datos.y == SOBREVIVE).sum())
    sin_edad = sum(f["edad"] is None for f in datos.filas)
    p.nota(f"{n} pasajeros; sobrevivieron {vivos} ({_pct(vivos / n)}). Responder siempre «no sobrevive» acierta "
           f"{n - vivos} de {n}: el {_pct((n - vivos) / n)}. Esa es la línea base que cualquier regla debe superar.\n"
           f"De {sin_edad} pasajeros no se conoce la edad.", "info", "Los pasajeros")


def _leer_csv(ruta: Path) -> list:
    """Lee un CSV de Excel o de otro programa: separado por comas o por punto y coma, en UTF-8 o en la codificación de Windows."""
    datos = ruta.read_bytes()
    for codificacion in ("utf-8-sig", "cp1252"):
        try:
            texto = datos.decode(codificacion)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ErrorDeLaboratorio(f"{ruta.name} no es un archivo de texto. Ábralo en Excel y guárdelo como «CSV UTF-8 "
                                 "(delimitado por comas)».")
    primera = texto.splitlines()[0] if texto.strip() else ""
    separador = ";" if primera.count(";") > primera.count(",") else ","
    filas = list(csv.DictReader(io.StringIO(texto), delimiter=separador))
    return [{(k or "").strip(): (v or "").strip() for k, v in f.items() if k is not None} for f in filas]


def _a_numero(texto: str):
    try:
        return float(texto.replace(",", "."))
    except ValueError:
        return None


@_amable
def cargar_casos(ruta, mostrar: bool = True) -> Datos | None:
    """Lee un CSV propio con columnas de datos y una columna «conclusion», para el trabajo independiente TI-1."""
    ruta = Path(ruta)
    if ruta.suffix.lower() in (".xlsx", ".xls", ".ods", ".numbers"):
        raise ErrorDeLaboratorio(f"{ruta.name} es una hoja de cálculo, no un CSV. Ábrala y guárdela como «CSV UTF-8 "
                                 f"(delimitado por comas)», con el nombre {ruta.stem}.csv, y escriba esa ruta.")
    if not ruta.exists():
        if (CARPETA_CASOS / ruta.name).exists() and ruta.parent != CARPETA_CASOS:
            raise ErrorDeLaboratorio(f"No encontré {ruta}, pero sí {CARPETA_CASOS / ruta.name}: escriba la ruta completa, "
                                     f"\"{(CARPETA_CASOS / ruta.name).as_posix()}\".")
        hay = sorted(f.name for f in CARPETA_CASOS.glob("*.csv")) if CARPETA_CASOS.exists() else []
        p.nota(f"No encontré {ruta}. " + (f"En mis_casos/ hay: {', '.join(hay)}. " if hay else "")
               + "Si todavía no tiene sus casos, siga los pasos de mis_casos/LEEME.md y ejecute de nuevo.",
               "info", "Sin casos propios")
        return None
    try:
        filas = _leer_csv(ruta)
    except (csv.Error, IndexError, UnicodeDecodeError) as e:
        raise ErrorDeLaboratorio(f"No pude leer {ruta} como CSV ({e}). Guárdelo desde Excel como «CSV UTF-8».") from None
    # la columna de la conclusión se reconoce con o sin tilde y con o sin mayúsculas; las demás conservan su nombre
    clave = next((k for k in (filas[0] if filas else {}) if _normal(k).replace(" ", "_") == "conclusion"), None)
    if clave is None:
        columnas = ", ".join(f"«{k}»" for k in (filas[0] if filas else {})) or "ninguna"
        raise ErrorDeLaboratorio(f"El archivo {ruta} debe tener una columna «conclusion» en la primera fila, con la "
                                 f"decisión del experto en cada caso (encontré: {columnas}).")
    filas = [{("conclusion" if k == clave else k): v for k, v in f.items()} for f in filas]
    nombres = [k for k in filas[0] if k and k != "conclusion"]
    if not 1 <= len(nombres) <= 10:
        raise ErrorDeLaboratorio(f"Use de 1 a 10 columnas de datos, además de «conclusion»; el archivo tiene {len(nombres)}.")
    filas = [f for f in filas if any(f.get(k) for k in nombres + ["conclusion"])]
    vacias = [str(i + 2) for i, f in enumerate(filas) if not f["conclusion"] or any(not f.get(k) for k in nombres)]
    if vacias:
        raise ErrorDeLaboratorio("Hay celdas vacías en las filas " + ", ".join(vacias[:10]) + (" …" if len(vacias) > 10 else "")
                                 + " (la fila 1 es la de los nombres). Llénelas o borre esas filas.")
    if len(filas) < 10:
        raise ErrorDeLaboratorio(f"El archivo tiene {len(filas)} casos; se necesitan al menos 10, y el TI-1 pide de 40 a 60.")
    clases = sorted({f["conclusion"] for f in filas})
    cuentas = {k: sum(f["conclusion"] == k for f in filas) for k in clases}
    if not 2 <= len(clases) <= 8:
        raise ErrorDeLaboratorio(f"Use de 2 a 8 conclusiones distintas; el archivo tiene {len(clases)}: {', '.join(clases)}.")
    solas = [f"«{k}»" for k, v in cuentas.items() if v < 2]
    if solas:
        raise ErrorDeLaboratorio("Cada conclusión necesita al menos 2 casos para la validación cruzada (mejor 5 o más). "
                                 "Tienen un solo caso: " + ", ".join(solas) + ".")
    columnas, X = [], np.zeros((len(filas), 0))
    for k in nombres:
        numeros = [_a_numero(f[k]) for f in filas]
        if all(v is not None for v in numeros):
            enteros = all(float(v).is_integer() for v in numeros)
            columnas.append({"clave": k, "tipo": "entera" if enteros else "real", "nombre": k, "unidad": ""})
            X = np.column_stack([X, numeros])
        else:
            valores = sorted({f[k] for f in filas})
            if len(valores) > 12:
                raise ErrorDeLaboratorio(f"La columna «{k}» tiene {len(valores)} textos distintos. Si son números, revise "
                                         "que no haya letras o espacios; si son categorías, use pocas (hasta 12).")
            for v in valores:
                columnas.append({"clave": f"{k} = {v}", "tipo": "categoria", "grupo": k, "valor": v, "valores": valores})
                X = np.column_stack([X, [1.0 if f[k] == v else 0.0 for f in filas]])
    datos = Datos(f"casos propios ({ruta.name})", X.astype(float), np.array([f["conclusion"] for f in filas]), columnas,
                  clases, filas, propio=True, tarea=f"casos propios ({ruta.name})")
    if mostrar:
        p.mostrar_tabla([{**{"caso": i + 1}, **{k: f[k] for k in nombres}, "conclusión": f["conclusion"]}
                         for i, f in enumerate(filas[:8])], titulo=f"Los primeros casos de {ruta.name}")
        resumen = ", ".join(f"«{k}»: {v}" for k, v in cuentas.items())
        tipos = ", ".join(f"{k} ({'número' if any(c['clave'] == k for c in columnas) else 'categoría'})" for k in nombres)
        partes = _partes(datos)
        p.nota(f"{len(filas)} casos. Conclusiones: {resumen}.\nColumnas: {tipos}.\nLa validación cruzada usará "
               f"{partes} partes" + ("." if partes == 5 else ": alguna conclusión tiene menos de 5 casos.")
               + (" Con menos de 30 casos, los resultados cambian mucho de una partición a otra." if len(filas) < 30 else ""),
               "info", "Sus casos")
    return datos


@_amable
def quitar_casos(datos: Datos, cantidad: int = 5) -> Datos | None:
    """Devuelve los mismos datos sin algunos casos elegidos al azar (con la semilla fija), para probar la estabilidad."""
    if datos is None:
        raise ErrorDeLaboratorio("Primero cargue los casos (la celda anterior).")
    if isinstance(cantidad, bool) or not isinstance(cantidad, int) or not 1 <= cantidad <= len(datos.y) // 3:
        raise ErrorDeLaboratorio(f"QUITAR_CASOS debe ser un número entero entre 1 y {len(datos.y) // 3}, sin comillas.")
    azar = np.random.default_rng(SEMILLA)
    for _ in range(200):          # se evita dejar una conclusión con menos de 2 casos
        quitar = set(int(i) for i in azar.choice(len(datos.y), cantidad, replace=False))
        quedan = np.array([i not in quitar for i in range(len(datos.y))])
        if min(int((datos.y[quedan] == k).sum()) for k in datos.clases) >= 2:
            break
    nuevos = Datos(datos.nombre + f" sin {cantidad} casos", datos.X[quedan], datos.y[quedan], datos.columnas, datos.clases,
                   [f for f, q in zip(datos.filas, quedan) if q], datos.propio, datos.tarea)
    p.nota("Se quitaron los casos " + ", ".join(str(i + 1) for i in sorted(quitar)) + f"; quedan {len(nuevos.y)}.", "info")
    return nuevos


@_amable
def estabilidad(datos: Datos, cantidad: int = 5, profundidad=3):
    """Quita algunos casos al azar, siempre los mismos, e induce otra vez el árbol: ¿se sostienen sus reglas?"""
    if datos is None:
        raise ErrorDeLaboratorio("Primero cargue los casos (la primera celda de esta sección).")
    nuevos = quitar_casos(datos, cantidad)
    return None if nuevos is None else arbol(nuevos, profundidad)


# ------------------------------------------------------------------ la regla del experto

def _validar_numero(nombre: str, valor, minimo: float, maximo: float, entero: bool = False, puede_faltar: bool = False) -> float:
    """Revisa un número de la configuración; con puede_faltar, los mensajes recuerdan que None es «desconocido»."""
    otra = " Si no se conoce, escriba None, sin comillas." if puede_faltar else ""
    if isinstance(valor, str):
        raise ErrorDeLaboratorio(f"{nombre} es un número: escríbalo sin comillas.{otra}")
    if isinstance(valor, tuple):
        raise ErrorDeLaboratorio(f"{nombre} quedó como dos números: ¿escribió una coma decimal? Use punto, por ejemplo 9.5.")
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) or math.isnan(valor):
        raise ErrorDeLaboratorio(f"{nombre} debe ser un número.{otra}")
    if entero and not float(valor).is_integer():
        raise ErrorDeLaboratorio(f"{nombre} debe ser un número entero, como {int(valor)}.")
    if not minimo <= valor <= maximo:
        raise ErrorDeLaboratorio(f"{nombre} debe estar entre {_n(minimo)} y {_n(maximo)}; escribió {valor}.{otra}")
    return valor


@_amable
def regla_del_experto(datos: Datos, edad_nino=14) -> dict | None:
    """Aplica «mujeres y niños primero» a todos los pasajeros y muestra cuántos acierta, por grupo."""
    if datos is None or datos.propio:
        raise ErrorDeLaboratorio("La regla del experto es para los pasajeros del Titanic: ejecute antes la sección 1.")
    edad_nino = _validar_numero("EDAD_NINO", edad_nino, 1, 80)
    mujer = datos.X[:, 1] == 1
    edad = datos.X[:, 2]
    nino = ~mujer & ~np.isnan(edad) & (edad < edad_nino)
    resto = ~mujer & ~nino
    pred = np.where(mujer | nino, SOBREVIVE, NO_SOBREVIVE)
    vive = datos.y == SOBREVIVE
    grupos = [("Mujeres", mujer, SOBREVIVE), (f"Niños: varones de menos de {_n(edad_nino, 0 if float(edad_nino).is_integer() else 1)} años", nino, SOBREVIVE),
              ("Los demás varones (o sin edad conocida)", resto, NO_SOBREVIVE)]
    tabla = []
    for nombre, m, dice in grupos:
        aciertos = int((vive[m] if dice == SOBREVIVE else ~vive[m]).sum())
        tabla.append({"grupo": nombre, "pasajeros": int(m.sum()), "sobrevivieron": int(vive[m].sum()),
                      "la regla dice": dice, "aciertos": f"{aciertos} de {int(m.sum())}"
                      + (f" ({_pct(aciertos / m.sum(), 0)})" if m.sum() else "")})
    total = int((pred == datos.y).sum())
    tabla.append({"grupo": "Total", "pasajeros": len(datos.y), "sobrevivieron": int(vive.sum()), "la regla dice": "",
                  "aciertos": f"{total} de {len(datos.y)} ({_pct(total / len(datos.y))})"})
    base = int((~vive).sum())
    tabla.append({"grupo": "Referencia: responder siempre «no sobrevive»", "pasajeros": len(datos.y), "sobrevivieron": "",
                  "la regla dice": NO_SOBREVIVE, "aciertos": f"{base} de {len(datos.y)} ({_pct(base / len(datos.y))})"})
    p.mostrar_tabla(tabla, titulo="La regla del experto: «mujeres y niños primero»")
    edad_texto = _n(edad_nino, 0 if float(edad_nino).is_integer() else 1)
    _registrar(datos, "regla del experto", f"mujeres y niños de menos de {edad_texto} años", "local",
               "regla escrita a mano", pred, segundos=0.0)
    _ESTADO["experto"] = total / len(datos.y)
    return {"acierto": total / len(datos.y), "prediccion": pred}


# ------------------------------------------------------------------ árboles, reglas y validación cruzada

def _validar_profundidad(valor, nombre: str = "PROFUNDIDAD"):
    if valor is None:
        return None
    if isinstance(valor, str):
        if _normal(valor) in ("none", "sin limite", "ninguna"):
            raise ErrorDeLaboratorio(f"Para un árbol sin límite de profundidad, escriba None sin comillas, no {valor!r}.")
        raise ErrorDeLaboratorio(f"{nombre} es un número entero, sin comillas, o None para «sin límite».")
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not float(valor).is_integer():
        raise ErrorDeLaboratorio(f"{nombre} debe ser un número entero, como 3, o None para «sin límite»; escribió {valor!r}.")
    if not 1 <= valor <= 30:
        raise ErrorDeLaboratorio(f"{nombre} debe estar entre 1 y 30, o ser None; escribió {valor}.")
    return int(valor)


def _partes(datos: Datos) -> int:
    """Cuántas partes usa la validación cruzada: 5, o menos si alguna conclusión tiene pocos casos."""
    menor = min(int((datos.y == k).sum()) for k in datos.clases)
    return max(2, min(5, menor))


def _validacion(modelo, datos: Datos):
    """Validación cruzada estratificada con semilla fija: el acierto de cada parte y la predicción de cada caso
    hecha por el modelo que no lo vio."""
    from sklearn.base import clone
    from sklearn.model_selection import StratifiedKFold
    cv = StratifiedKFold(_partes(datos), shuffle=True, random_state=SEMILLA)
    aciertos, prediccion = [], np.empty(len(datos.y), dtype=object)
    for entrenar, probar in cv.split(datos.X, datos.y):
        m = clone(modelo).fit(datos.X[entrenar], datos.y[entrenar])
        pred = m.predict(datos.X[probar])
        prediccion[probar] = pred
        aciertos.append(float((pred == datos.y[probar]).mean()))
    return np.array(aciertos), prediccion.astype(str)


def _texto_umbral(columna: dict, umbral: float) -> str:
    if columna["tipo"] == "entera":
        return _n(math.floor(umbral))
    return _n(umbral, 1) + columna.get("unidad", "")


def _condicion_nodo(columna: dict, umbral: float):
    """La pregunta de un nodo y los rótulos de sus ramas (izquierda: se cumple «columna ≤ umbral»).

    Un umbral infinito separa los casos con el dato, a la izquierda, de los que no lo tienen, a la derecha."""
    tipo = columna["tipo"]
    if math.isinf(umbral):
        return f"¿{columna['nombre']} {columna['conocida']}?", "sí", "no"
    if tipo == "binaria":
        return columna["pregunta"], "no", "sí"
    if tipo == "categoria":
        return f"¿{columna['grupo']} = {columna['valor']}?", "no", "sí"
    if tipo == "ordinal":
        incluidas = [e for v, e in columna["etiquetas"].items() if v <= umbral]
        return f"¿{' o '.join(incluidas)} {columna['nombre']}?", "sí", "no"
    if tipo == "entera":
        return f"¿{columna['nombre']} ≤ {_texto_umbral(columna, umbral)}?", "sí", "no"
    return f"¿{columna['nombre']} ≤ {_texto_umbral(columna, umbral)}?", "sí", "no"


def _hijos(t, nodo: int, columna: dict) -> list:
    """Los dos hijos de un nodo, primero el del «sí»: en las preguntas de sí o no, como ¿mujer?, scikit-learn lo pone
    a la derecha; en las de «≤», a la izquierda. Así el dibujo y las reglas leen siempre el «sí» primero."""
    izquierda, derecha = (int(t.children_left[nodo]), "izquierda"), (int(t.children_right[nodo]), "derecha")
    return [derecha, izquierda] if columna["tipo"] in ("binaria", "categoria") else [izquierda, derecha]


def _texto_condicion(columna: dict, limites: dict) -> str | None:
    """Une las preguntas de un camino sobre una misma columna en una sola condición legible."""
    tipo, bajo, alto = columna["tipo"], limites["bajo"], limites["alto"]
    if limites.get("solo_faltante"):
        return f"{columna['nombre']} {columna['faltante']}"
    if tipo == "binaria":
        if bajo >= 0.5:
            return columna["si"]
        if alto <= 0.5:
            return columna["no"]
        return None
    if tipo == "ordinal":
        incluidas = [e for v, e in columna["etiquetas"].items() if bajo < v <= alto]
        return f"{' o '.join(incluidas)} {columna['nombre']}"
    if tipo == "entera":
        desde = None if bajo == -math.inf else math.floor(bajo) + 1
        hasta = None if alto == math.inf else math.floor(alto)
        nombre = columna["nombre"]
        if desde is not None and hasta is not None:
            texto = f"{nombre} = {desde}" if desde == hasta else f"{nombre} entre {desde} y {hasta}"
        elif hasta is not None:
            texto = f"{nombre} ≤ {hasta}"
        elif desde is not None:
            texto = f"{nombre} ≥ {desde}"
        else:
            return None
    else:
        nombre, u = columna["nombre"], columna.get("unidad", "")
        if bajo != -math.inf and alto != math.inf:
            texto = f"{nombre} > {_n(bajo, 1)}{u} y ≤ {_n(alto, 1)}{u}"
        elif alto != math.inf:
            texto = f"{nombre} ≤ {_n(alto, 1)}{u}"
        elif bajo != -math.inf:
            texto = f"{nombre} > {_n(bajo, 1)}{u}"
        elif limites.get("conocida"):
            return f"{nombre} {columna['conocida']}"
        else:
            return None
    if columna.get("puede_faltar") and limites["faltante"]:
        texto += f" o {columna['faltante']}"
    return texto


def _textos_categoria(columnas: list, grupos: dict) -> dict:
    """Las condiciones sobre columnas de categorías: «= valor», o los valores que quedan si solo se sabe qué no es."""
    textos = {}
    for grupo, (es, no_es) in grupos.items():
        valores = next(c["valores"] for c in columnas if c.get("grupo") == grupo)
        if es:
            textos[grupo] = f"{grupo} = {es}"
        else:
            quedan = [v for v in valores if v not in no_es]
            textos[grupo] = f"{grupo} = {quedan[0]}" if len(quedan) == 1 else f"{grupo} = {', '.join(quedan[:-1])} o {quedan[-1]}"
    return textos


def _faltan_en_nodo(modelo, X) -> dict:
    """Para cada nodo, si alguno de los casos que pasan por él no tiene el dato que el nodo pregunta."""
    t = modelo.tree_
    camino = modelo.decision_path(X).tocsc()
    faltan = {}
    for i in range(t.node_count):
        if t.children_left[i] != -1:
            casos = camino[:, i].nonzero()[0]
            faltan[i] = bool(np.isnan(X[casos, t.feature[i]]).any())
    return faltan


def reglas_del_arbol(modelo, datos: Datos) -> list:
    """Cada camino de la raíz a una hoja, como una regla SI… ENTONCES con los casos de entrenamiento que llegan a ella.

    «o desconocida» aparece solo en las condiciones por las que pasaron casos sin ese dato."""
    t = modelo.tree_
    faltan = getattr(t, "missing_go_to_left", None)
    con_faltantes = _faltan_en_nodo(modelo, datos.X)
    reglas = []

    def recorrer(nodo, camino):
        if t.children_left[nodo] == -1:
            cuentas = t.value[nodo][0] * t.n_node_samples[nodo]
            k = int(np.argmax(cuentas))
            orden, limites, grupos = [], {}, {}
            for col, direccion, umbral, falta_aqui in camino:
                columna = datos.columnas[col]
                if columna["tipo"] == "categoria":
                    es, no_es = grupos.setdefault(columna["grupo"], [None, set()])
                    if direccion == "derecha":
                        grupos[columna["grupo"]][0] = columna["valor"]
                    else:
                        no_es.add(columna["valor"])
                    if ("g", columna["grupo"]) not in orden:
                        orden.append(("g", columna["grupo"]))
                    continue
                lim = limites.setdefault(col, {"bajo": -math.inf, "alto": math.inf, "faltante": True})
                if math.isinf(umbral):            # la pregunta «¿edad conocida?»
                    lim["conocida" if direccion == "izquierda" else "solo_faltante"] = True
                elif direccion == "izquierda":
                    lim["alto"] = min(lim["alto"], umbral)
                else:
                    lim["bajo"] = max(lim["bajo"], umbral)
                lim["faltante"] = lim["faltante"] and falta_aqui
                if ("c", col) not in orden:
                    orden.append(("c", col))
            categorias = _textos_categoria(datos.columnas, grupos)
            partes = []
            for clase, clave in orden:
                texto = categorias[clave] if clase == "g" else _texto_condicion(datos.columnas[clave], limites[clave])
                if texto:
                    partes.append(texto)
            reglas.append({"si": " Y ".join(partes), "entonces": str(modelo.classes_[k]),
                           "casos": int(t.n_node_samples[nodo]), "aciertos": int(round(cuentas[k])), "hoja": nodo})
            return
        col, umbral = t.feature[nodo], float(t.threshold[nodo])
        izquierda_faltan = bool(faltan[nodo]) if faltan is not None else False
        hay = con_faltantes.get(nodo, False)
        for hijo, direccion in _hijos(t, nodo, datos.columnas[col]):
            falta = hay and (izquierda_faltan if direccion == "izquierda" else not izquierda_faltan)
            recorrer(hijo, camino + [(col, direccion, umbral, falta)])

    recorrer(0, [])
    return reglas


def _nodos_para_dibujo(modelo, datos: Datos) -> list:
    t = modelo.tree_
    faltan = getattr(t, "missing_go_to_left", None)
    con_faltantes = _faltan_en_nodo(modelo, datos.X)
    nodos = []
    for i in range(t.node_count):
        if t.children_left[i] == -1:
            cuentas = t.value[i][0] * t.n_node_samples[i]
            k = int(np.argmax(cuentas))
            nodos.append({"id": i, "hoja": True, "clase": str(modelo.classes_[k]), "aciertos": int(round(cuentas[k])),
                          "casos": int(t.n_node_samples[i])})
        else:
            columna = datos.columnas[t.feature[i]]
            umbral = float(t.threshold[i])
            pregunta, izq, der = _condicion_nodo(columna, umbral)
            if columna.get("puede_faltar") and faltan is not None and con_faltantes.get(i) and not math.isinf(umbral):
                if faltan[i]:
                    izq += f" o {columna['faltante']}"
                else:
                    der += f" o {columna['faltante']}"
            rotulos = {"izquierda": izq, "derecha": der}
            (primero, lado_1), (segundo, lado_2) = _hijos(t, i, columna)
            nodos.append({"id": i, "hoja": False, "pregunta": pregunta, "izquierda": primero, "derecha": segundo,
                          "rotulo_izquierda": rotulos[lado_1], "rotulo_derecha": rotulos[lado_2]})
    return nodos


def _mostrar_reglas(reglas: list, datos: Datos, titulo: str) -> None:
    palabra = "pasajeros" if not datos.propio else "casos"
    filas = [{"#": i + 1, "regla": f"SI {r['si'] or '(siempre)'} ENTONCES {r['entonces']}",
              palabra: r["casos"], "la regla acierta": f"{r['aciertos']} de {r['casos']} ({_pct(r['aciertos'] / r['casos'], 0)})"}
             for i, r in enumerate(reglas)]
    p.mostrar_tabla(filas, titulo=titulo)


@_amable
def arbol(datos: Datos, profundidad=3, mostrar: bool = True, registrar: bool = True):
    """Induce un árbol de decisión, lo dibuja, lo traduce a reglas y lo evalúa con validación cruzada."""
    if datos is None:
        raise ErrorDeLaboratorio("Primero cargue los datos (la sección 1, o la celda de sus casos).")
    _sklearn()
    from sklearn.tree import DecisionTreeClassifier
    profundidad = _validar_profundidad(profundidad, "PROFUNDIDAD_MIS_CASOS" if datos.propio else "PROFUNDIDAD")
    inicio = time.perf_counter()
    modelo = DecisionTreeClassifier(max_depth=profundidad, random_state=SEMILLA).fit(datos.X, datos.y)
    aciertos, prediccion = _validacion(DecisionTreeClassifier(max_depth=profundidad, random_state=SEMILLA), datos)
    segundos = time.perf_counter() - inicio
    reglas = reglas_del_arbol(modelo, datos)
    texto_prof = "sin límite" if profundidad is None else str(profundidad)
    if mostrar:
        if modelo.get_n_leaves() <= 16:
            graficas.dibujar_arbol(_nodos_para_dibujo(modelo, datos), datos.clases,
                                   f"Árbol de profundidad {texto_prof} · {datos.nombre}")
        else:
            p.nota(f"El árbol tiene {modelo.get_n_leaves()} hojas: es demasiado grande para dibujarlo. Abajo están sus "
                   "primeras reglas.", "info")
        muestra = reglas if len(reglas) <= 16 else reglas[:16]
        _mostrar_reglas(muestra, datos, f"Sus reglas: una por cada hoja ({len(reglas)} en total)"
                        + ("" if len(reglas) <= 16 else ", se muestran las 16 primeras"))
        graficas.partes_validacion(aciertos, f"Validación cruzada de {len(aciertos)} partes · árbol de profundidad {texto_prof}")
        referencia = []
        if not datos.propio and "experto" in _ESTADO:
            referencia.append(f"la regla del experto acertó el {_pct(_ESTADO['experto'])}")
        base = (datos.y == datos.mayoritaria).mean()
        referencia.append(f"responder siempre «{datos.mayoritaria}» acierta el {_pct(base)}")
        p.nota(f"El árbol acierta, en promedio, el {_pct(aciertos.mean())} de los casos que no vio (de {_pct(aciertos.min())} "
               f"a {_pct(aciertos.max())} según la parte). Como referencia, " + " y ".join(referencia) + ".", "exito",
               "En casos que el árbol no vio")
    if registrar and not datos.propio:          # el CSV del contrapunto es solo del Titanic
        _registrar(datos, "árbol de decisión", f"profundidad {texto_prof}", "local",
                   "DecisionTreeClassifier (scikit-learn)", prediccion, segundos)
        _ESTADO["arbol"] = modelo
        _ESTADO["arbol_cv"] = float(aciertos.mean())
        _ESTADO["profundidad"] = texto_prof
    return {"modelo": modelo, "reglas": reglas, "validacion": aciertos, "prediccion": prediccion}


@_amable
def curva_profundidad(datos: Datos, profundidades) -> list | None:
    """Entrena un árbol por cada profundidad y compara su acierto en entrenamiento y en validación cruzada."""
    if datos is None:
        raise ErrorDeLaboratorio("Primero cargue los datos.")
    _sklearn()
    from sklearn.tree import DecisionTreeClassifier
    if isinstance(profundidades, tuple):
        raise ErrorDeLaboratorio("Escriba las profundidades entre corchetes, separadas por comas: [1, 2, 3, 5, 8, None].")
    if not isinstance(profundidades, list) or not profundidades:
        raise ErrorDeLaboratorio("PROFUNDIDADES debe ser una lista entre corchetes, por ejemplo [1, 2, 3, 5, 8, None].")
    vistos, lista = set(), []
    for v in profundidades:
        d = _validar_profundidad(v, "Cada profundidad de la lista")
        if d not in vistos:
            vistos.add(d)
            lista.append(d)
    lista.sort(key=lambda d: math.inf if d is None else d)
    filas = []
    for d in lista:
        aciertos, _ = _validacion(DecisionTreeClassifier(max_depth=d, random_state=SEMILLA), datos)
        modelo = DecisionTreeClassifier(max_depth=d, random_state=SEMILLA).fit(datos.X, datos.y)
        filas.append({"profundidad": "sin límite" if d is None else d, "hojas": int(modelo.get_n_leaves()),
                      "entrenamiento": float((modelo.predict(datos.X) == datos.y).mean()),
                      "validacion": float(aciertos.mean()), "desviacion": float(aciertos.std())})
    mejor = max(filas, key=lambda f: f["validacion"])
    graficas.curva_profundidad(filas, mejor, datos.nombre)
    p.mostrar_tabla([{"profundidad": f["profundidad"], "hojas (reglas)": f["hojas"],
                      "acierto en entrenamiento": _pct(f["entrenamiento"]),
                      "acierto en validación cruzada": _pct(f["validacion"]),
                      "variación entre partes": f"± {_n(100 * f['desviacion'], 1)}"}
                     for f in filas], titulo="Profundidad, tamaño y acierto")
    return filas


@_amable
def ensambles(datos: Datos, arboles_del_bosque: int = 300) -> list | None:
    """Compara el árbol de la sección 2 con un bosque aleatorio y un boosting por gradiente, con la misma validación."""
    if datos is None:
        raise ErrorDeLaboratorio("Primero cargue los datos.")
    _sklearn()
    from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
    from sklearn.tree import DecisionTreeClassifier
    profundidad = _ESTADO.get("profundidad", "3") if not datos.propio else "3"
    d = None if profundidad == "sin límite" else int(profundidad)
    modelos = [(f"Un árbol de profundidad {profundidad}", "árbol de decisión", f"profundidad {profundidad}",
                DecisionTreeClassifier(max_depth=d, random_state=SEMILLA)),
               (f"Bosque aleatorio de {arboles_del_bosque} árboles", "bosque aleatorio", f"{arboles_del_bosque} árboles",
                RandomForestClassifier(arboles_del_bosque, min_samples_leaf=3, random_state=SEMILLA)),
               ("Boosting por gradiente", "boosting por gradiente", "árboles en serie",
                HistGradientBoostingClassifier(random_state=SEMILLA))]
    filas = []
    for nombre, metodo, estrategia, modelo in modelos:
        inicio = time.perf_counter()
        aciertos, prediccion = _validacion(modelo, datos)
        completo = modelo.fit(datos.X, datos.y)
        segundos = time.perf_counter() - inicio
        if metodo == "árbol de decisión":
            caminos = int(completo.get_n_leaves())
            leer = f"{caminos} reglas"
        elif metodo == "bosque aleatorio":
            caminos = sum(int(a.get_n_leaves()) for a in completo.estimators_)
            leer = f"{_n(caminos)} reglas en {arboles_del_bosque} árboles que votan"
            _ESTADO["bosque"] = completo if not datos.propio else _ESTADO.get("bosque")
        else:
            leer = f"{completo.n_iter_} árboles en serie, de hasta 31 hojas; cada uno corrige al anterior"
        filas.append({"modelo": nombre, "acierto (validación cruzada)": _pct(aciertos.mean()),
                      "variación entre partes": f"± {_n(100 * aciertos.std(), 1)}", "lo que habría que leer": leer,
                      "tiempo": "menos de 1 s" if segundos < 1 else f"{_n(segundos, 1)} s"})
        if metodo != "árbol de decisión" and not datos.propio:
            _registrar(datos, metodo, estrategia, "local", type(modelo).__name__ + " (scikit-learn)", prediccion, segundos)
    p.mostrar_tabla(filas, titulo=f"Un árbol frente a dos ensambles · {datos.nombre}")
    return filas


@_amable
def pregunta_del_auditor(datos: Datos, pasajero: dict) -> None:
    """Muestra el camino del árbol que lleva a la predicción de un pasajero, y lo que dice el bosque, que no tiene camino."""
    if datos is None or datos.propio:
        raise ErrorDeLaboratorio("La pregunta del auditor usa los pasajeros del Titanic.")
    if "arbol" not in _ESTADO or "bosque" not in _ESTADO:
        raise ErrorDeLaboratorio("Antes ejecute la sección 2 (el árbol) y la celda de los ensambles de esta sección.")
    if not isinstance(pasajero, dict):
        raise ErrorDeLaboratorio("PASAJERO debe ir entre llaves { }, con los datos del pasajero, como en el ejemplo.")
    claves = ["clase", "sexo", "edad", "hermanos_o_conyuge", "padres_o_hijos", "tarifa", "puerto"]
    faltan = [k for k in claves if k not in pasajero]
    sobran = [k for k in pasajero if k not in claves]
    if faltan or sobran:
        raise ErrorDeLaboratorio(("Faltan datos: " + ", ".join(faltan) + ". " if faltan else "")
                                 + ("No reconozco: " + ", ".join(sobran) + ". " if sobran else "")
                                 + "Use las claves del ejemplo, escritas igual: " + ", ".join(claves) + ".")
    if isinstance(pasajero["clase"], bool) or pasajero["clase"] not in (1, 2, 3):
        raise ErrorDeLaboratorio(f"clase debe ser 1, 2 o 3, sin comillas ni «.ª»; escribió {pasajero['clase']!r}.")
    clase = int(pasajero["clase"])
    sexo = _normal(pasajero["sexo"]) if isinstance(pasajero["sexo"], str) else ""
    if sexo not in ("mujer", "hombre"):
        raise ErrorDeLaboratorio("sexo debe ser \"mujer\" o \"hombre\", entre comillas.")
    edad = None if pasajero["edad"] is None else _validar_numero("edad", pasajero["edad"], 0, 100, puede_faltar=True)
    hermanos = _validar_numero("hermanos_o_conyuge", pasajero["hermanos_o_conyuge"], 0, 10, entero=True)
    padres = _validar_numero("padres_o_hijos", pasajero["padres_o_hijos"], 0, 10, entero=True)
    tarifa = None if pasajero["tarifa"] is None else _validar_numero("tarifa", pasajero["tarifa"], 0, 600, puede_faltar=True)
    puertos = {_normal(v): v for v in PUERTOS.values()}
    if not isinstance(pasajero["puerto"], str) or _normal(pasajero["puerto"]) not in puertos:
        raise ErrorDeLaboratorio("puerto debe ser \"Southampton\", \"Cherbourg\" o \"Queenstown\", entre comillas.")
    puerto = puertos[_normal(pasajero["puerto"])]
    x = np.array([[clase, 1.0 if sexo == "mujer" else 0.0, np.nan if edad is None else edad, hermanos, padres,
                   np.nan if tarifa is None else tarifa, 1.0 if puerto == "Cherbourg" else 0.0,
                   1.0 if puerto == "Queenstown" else 0.0]])
    modelo, t = _ESTADO["arbol"], _ESTADO["arbol"].tree_
    faltan_izq = getattr(t, "missing_go_to_left", None)
    nodo, pasos = 0, []
    while t.children_left[nodo] != -1:
        columna = datos.columnas[t.feature[nodo]]
        pregunta, izq, der = _condicion_nodo(columna, float(t.threshold[nodo]))
        valor = x[0, t.feature[nodo]]
        if np.isnan(valor):
            va_izquierda = bool(faltan_izq[nodo]) if faltan_izq is not None else True
            dato = columna["faltante"]
            respuesta = (izq if va_izquierda else der) + ("" if math.isinf(t.threshold[nodo]) else f" o {columna['faltante']}")
        else:
            va_izquierda = valor <= t.threshold[nodo]
            dato = {"mujer": sexo, "clase": f"{clase}.ª", "embarco_en_C": puerto, "embarco_en_Q": puerto}.get(
                columna["clave"], _n(valor, 0 if float(valor).is_integer() else 2) + columna.get("unidad", ""))
            respuesta = izq if va_izquierda else der
        pasos.append({"paso": len(pasos) + 1, "pregunta del árbol": pregunta, "dato del pasajero": dato,
                      "respuesta": respuesta})
        nodo = t.children_left[nodo] if va_izquierda else t.children_right[nodo]
    cuentas = t.value[nodo][0] * t.n_node_samples[nodo]
    k = int(np.argmax(cuentas))
    vivos = int(round(cuentas[list(modelo.classes_).index(SOBREVIVE)]))
    p.mostrar_tabla(pasos, titulo=f"El camino del árbol de profundidad {_ESTADO['profundidad']} para este pasajero")
    casos = int(t.n_node_samples[nodo])
    p.nota(f"El árbol responde «{modelo.classes_[k]}» porque el pasajero llega a una hoja con {casos} "
           f"{'pasajero' if casos == 1 else 'pasajeros'}, de los que {'sobrevivió' if vivos == 1 else 'sobrevivieron'} "
           f"{vivos}. Esa es su explicación completa: el camino de arriba.",
           "exito", "Lo que responde el árbol")
    bosque = _ESTADO["bosque"]
    probabilidad = float(bosque.predict_proba(x)[0][list(bosque.classes_).index(SOBREVIVE)])
    indice = list(bosque.classes_).index(SOBREVIVE)
    votos = sum(int(a.predict(x)[0]) == indice for a in bosque.estimators_)
    p.nota(f"El bosque responde «{SOBREVIVE if probabilidad >= 0.5 else NO_SOBREVIVE}». De sus {len(bosque.estimators_)} "
           f"árboles, {votos} votan «sobrevive»; y si se promedia la proporción de sobrevivientes de la hoja a la que llega "
           f"en cada árbol, la probabilidad de sobrevivir es {_n(probabilidad, 2)}. Para explicarlo habría que mostrar "
           f"{len(bosque.estimators_)} caminos: no hay uno solo.", "aviso", "Lo que responde el bosque")


# ------------------------------------------------------------------ el CSV común del contrapunto

COLUMNAS_CSV = ["sesion", "laboratorio", "pareja", "fecha", "tarea", "instancia", "metodo", "estrategia", "proveedor",
                "modelo", "correcto", "resultado", "iteraciones", "llamadas", "tokens_entrada", "tokens_salida",
                "tokens_razonamiento", "costo_usd", "tiempo_s", "notas"]


def _registrar(datos: Datos, metodo: str, estrategia: str, proveedor: str, modelo: str, prediccion, segundos: float,
               llamadas: int = 0, tokens_entrada: int = 0, tokens_salida: int = 0, costo_usd: float = 0.0) -> None:
    """Anota una fila por caso: la llamada al LLM y sus tokens y costo van en la fila del primer caso."""
    for clave in [k for k in _REGISTRO if k[0] == metodo and k[1] == estrategia and k[2] == datos.huella]:
        del _REGISTRO[clave]
    for i, (real, dicho) in enumerate(zip(datos.y, prediccion)):
        primero = i == 0
        _REGISTRO[(metodo, estrategia, datos.huella, i)] = {
            "sesion": 6, "laboratorio": "6A", "fecha": date.today().isoformat(), "tarea": datos.tarea,
            "instancia": f"{'caso' if datos.propio else 'pasajero'} {i + 1}", "metodo": metodo, "estrategia": estrategia,
            "proveedor": proveedor, "modelo": modelo, "correcto": int(str(dicho) == str(real)),
            "resultado": str(dicho), "iteraciones": 1, "llamadas": llamadas if primero else 0,
            "tokens_entrada": tokens_entrada if primero else 0, "tokens_salida": tokens_salida if primero else 0,
            "tokens_razonamiento": 0, "costo_usd": round(costo_usd, 7) if primero else 0,
            "tiempo_s": round(segundos / len(datos.y), 5), "notas": f"real: {real}"}


def exportar_csv(pareja: str, ruta: str = ARCHIVO_CSV) -> None:
    """Escribe en el CSV común del contrapunto todos los métodos de esta sesión del kernel, con una fila por caso."""
    if not _REGISTRO:
        p.nota("No hay resultados para exportar: ejecute antes las secciones 1 a 5.", "aviso")
        return
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
        return
    grupos = {}
    for fila in _REGISTRO.values():
        g = grupos.setdefault((fila["tarea"], fila["metodo"], fila["estrategia"]), {"filas": 0, "aciertos": 0, "costo": 0.0})
        g["filas"] += 1
        g["aciertos"] += fila["correcto"]
        g["costo"] += float(fila["costo_usd"] or 0)
    p.mostrar_tabla([{"tarea": t, "método": m, "estrategia": e, "casos": g["filas"],
                      "aciertos": f"{g['aciertos']} ({_pct(g['aciertos'] / g['filas'])})", "costo (US$)": _n(g["costo"], 5)}
                     for (t, m, e), g in grupos.items()], titulo=f"{len(_REGISTRO)} filas guardadas en {destino}")
