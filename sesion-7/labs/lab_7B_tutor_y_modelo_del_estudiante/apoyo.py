"""Apoyo del Laboratorio 7B (Sesión 7, Sistemas Inteligentes): revisar lo que escribe la pareja y llevar la bitácora.

- Los errores de configuración se muestran en una caja roja, sin traza, con lo que hay que corregir.
- La bitácora resultados_7B.csv anota cada experimento. Conserva lo anotado aunque se reinicie el kernel.
- Los números se escriben con punto decimal, como en el código (Especializacion AI/normas.md).
"""
from __future__ import annotations

import csv
import io
import math
from datetime import date
from functools import wraps
from pathlib import Path

import presentacion as p

BITACORA = Path("resultados_7B.csv")
_COLUMNAS = ["fecha", "seccion", "experimento", "configuracion", "resultado", "valor"]
_FILAS: dict = {}


class ErrorDeLaboratorio(Exception):
    """Un problema que la pareja puede corregir: se muestra en una caja roja, sin traza."""


def amable(funcion):
    """Muestra los errores de configuración en una caja roja y devuelve None, en lugar de una traza larga."""
    @wraps(funcion)
    def envoltura(*args, **kwargs):
        try:
            return funcion(*args, **kwargs)
        except ErrorDeLaboratorio as e:
            p.nota(str(e), "error", "Revisa la configuración")
            return None
    return envoltura


# ----------------------------------------------------------------------------- números

def num(valor: float, decimales: int | None = None) -> str:
    """Un número con punto decimal y espacio para los miles: 1 000, 32.5, -0.22.

    Sin decimales fijos, usa uno desde 10 y dos por debajo, y quita los ceros que sobran."""
    if decimales is None:
        decimales = 1 if abs(valor) >= 10 else 2
    texto = f"{valor:,.{decimales}f}".replace(",", " ")
    if "." in texto:
        texto = texto.rstrip("0").rstrip(".")
    return "0" if texto in ("-0", "") else texto


def pct(prob: float) -> str:
    """Una probabilidad como porcentaje con un decimal: 0.2842 → 28.4 %. Las muy pequeñas llevan más cifras."""
    valor = prob * 100
    if 0 < abs(valor) < 0.05:
        return f"{valor:.2g} %"
    return f"{valor:.1f} %"


def prob(x: float) -> str:
    """Una probabilidad con dos decimales. Las muy pequeñas o muy cercanas a 1 llevan más cifras: 0.001 y 0.999."""
    if 0 < x < 0.005:
        return f"{x:.1g}"
    if 0.9995 <= x < 1:
        return "> 0.999"
    return f"{x:.3f}" if 0.995 < x < 1 else num(x, 2)


def _sugerir_punto(valor: tuple) -> str:
    """Si una coma decimal partió un número en dos, lo propone con punto: (0, 95) → 0.95."""
    if len(valor) == 2 and all(type(v) is int for v in valor) and valor[1] >= 0:
        signo = "-" if valor[0] < 0 else ""
        return f"{signo}{abs(valor[0])}.{valor[1]}"
    return "0.5"


def numero(nombre: str, valor, minimo: float = -math.inf, maximo: float = math.inf) -> float:
    """Revisa que un valor sea un número dentro del rango, y explica qué corregir si no lo es."""
    if isinstance(valor, str):
        raise ErrorDeLaboratorio(f"{nombre} es un número: escríbelo sin comillas. Escribiste {valor!r}.")
    if isinstance(valor, tuple):
        raise ErrorDeLaboratorio(f"{nombre} quedó como dos números. ¿Escribiste una coma decimal? "
                                 f"Usa punto: {_sugerir_punto(valor)}.")
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) or math.isnan(valor):
        raise ErrorDeLaboratorio(f"{nombre} debe ser un número. Escribiste {valor!r}.")
    if not minimo <= valor <= maximo:
        rango = (f"estar entre {num(minimo)} y {num(maximo)}" if math.isfinite(minimo) and math.isfinite(maximo)
                 else f"ser mayor o igual que {num(minimo)}" if math.isfinite(minimo) else f"ser menor o igual que {num(maximo)}")
        raise ErrorDeLaboratorio(f"{nombre} debe {rango}. Escribiste {valor}.")
    return float(valor)


def probabilidad(nombre: str, valor) -> float:
    """Revisa una probabilidad: un número de 0 a 1. Reconoce los porcentajes y las comas decimales."""
    if isinstance(valor, (int, float)) and not isinstance(valor, bool) and 2 <= valor <= 100:
        raise ErrorDeLaboratorio(f"{nombre} vale {valor}, y una probabilidad va de 0 a 1. ¿Escribiste un porcentaje? "
                                 f"{num(valor)} % se escribe {num(valor / 100, 4)}.")
    return numero(nombre, valor, 0, 1)


def lista(nombre: str, valor, ejemplo: str) -> list:
    """Revisa que el valor sea una lista entre corchetes, no vacía."""
    if isinstance(valor, tuple):
        raise ErrorDeLaboratorio(f"{nombre} quedó como varios valores sueltos. Escribe la lista entre corchetes, "
                                 f"como {ejemplo}.")
    if not isinstance(valor, list) or not valor:
        raise ErrorDeLaboratorio(f"{nombre} debe ser una lista entre corchetes, separada por comas, como {ejemplo}.")
    return valor


def lista_de_probabilidades(nombre: str, valores, ejemplo: str, aviso_uno: bool = False) -> list:
    """Una lista de probabilidades. Una coma decimal dentro de la lista no da error en Python: 0,02 se lee 0 y 2.

    aviso_uno: avisa si la lista trae un 1, que es el 100 %. Por ejemplo, una tasa de falla de 1 por el 1 %."""
    valores = lista(nombre, valores, ejemplo)
    for i in range(len(valores) - 1):
        a, b = valores[i], valores[i + 1]
        if type(a) is int and a == 0 and type(b) is int and 0 <= b <= 1:
            p.nota(f"{nombre} tiene un 0 seguido de un {b}. Si escribiste 0,{b}, Python lo leyó como dos números. "
                   f"Usa punto: 0.{b}. Si de verdad querías 0 y {b}, ignora este aviso.", "aviso", "Revisa la lista")
    if aviso_uno and any(type(v) is int and v == 1 for v in valores):
        p.nota(f"{nombre} tiene un 1, que es el 100 %. Si querías el 1 %, escribe 0.01.", "aviso", "Revisa la lista")
    for i, v in enumerate(valores):
        if type(v) is int and v > 1:
            if i and type(valores[i - 1]) is int and valores[i - 1] == 0:
                # 0,5 dentro de una lista se lee como dos números: 0 y 5
                raise ErrorDeLaboratorio(f"{nombre} tiene un 0 seguido de un {v}. ¿Escribiste una coma decimal, como "
                                         f"0,{v}? Python la lee como dos números. Usa punto: 0.{v}.")
            raise ErrorDeLaboratorio(f"{nombre} tiene un {v}, y una probabilidad va de 0 a 1. ¿Escribiste un porcentaje? "
                                     f"{v} % se escribe {num(v / 100, 4)}.")
    return [probabilidad(f"El valor {i + 1} de {nombre}", v) for i, v in enumerate(valores)]


def lista_de_numeros(nombre: str, valores, ejemplo: str, minimo: float = -math.inf) -> list:
    """Una lista de precios o de pagos. Un 0 entero o un valor repetido suelen venir de una coma decimal: 1,5 se lee 1 y 5."""
    valores = lista(nombre, valores, ejemplo)
    numeros = [numero(f"El valor {i + 1} de {nombre}", v, minimo) for i, v in enumerate(valores)]
    if any(type(v) is int and v == 0 for v in valores) or len(set(numeros)) < len(numeros):
        raise ErrorDeLaboratorio(f"{nombre} tiene un 0 o un valor repetido. ¿Escribiste una coma decimal, como 1,5? "
                                 f"Python la lee como dos números, 1 y 5. Usa punto: 1.5. "
                                 "Si de verdad quieres un cero, escribe 0.0.")
    for i in range(len(valores) - 1):
        a, b = valores[i], valores[i + 1]
        # 12,5 dentro de una lista se lee 12 y 5: un entero seguido de un dígito menor
        if type(a) is int and type(b) is int and 0 <= b <= 9 and b < abs(a):
            p.nota(f"{nombre} tiene un {a} seguido de un {b}. Si escribiste {a},{b}, Python lo leyó como dos números. "
                   f"Usa punto: {a}.{b}. Si de verdad querías {a} y {b}, ignora este aviso.", "aviso", "Revisa la lista")
    return numeros


def texto(nombre: str, valor) -> str:
    """Revisa que un nombre sea un texto entre comillas."""
    if not isinstance(valor, str) or not valor.strip():
        raise ErrorDeLaboratorio(f"{nombre} debe ser un texto entre comillas, como \"seco\". Escribiste {valor!r}.")
    return valor.strip()


# ----------------------------------------------------------------------------- la bitácora

def anotar(seccion: str, experimento: str, configuracion: str, resultado: str, valor) -> None:
    """Agrega o actualiza una fila de la bitácora y la guarda.

    La primera vez en cada sesión del kernel lee la bitácora que ya existe, para no borrar lo anotado antes.
    Un experimento repetido con la misma configuración reemplaza su fila."""
    if not _FILAS and BITACORA.exists():
        filas = _leer()
        if filas is None:
            respaldo = BITACORA.with_name(BITACORA.stem + "_respaldo.csv")
            try:
                BITACORA.replace(respaldo)
                p.nota(f"No pude leer la bitácora anterior, quizás porque la guardaste desde otro programa. Quedó como "
                       f"{respaldo.name} y empiezo una nueva. Entrega las dos.", "aviso", "La bitácora")
            except OSError:
                p.nota(f"No pude leer ni respaldar {BITACORA}. Ciérralo si está abierto en Excel y ejecuta de nuevo.",
                       "error")
                return
        for fila in filas or []:
            _FILAS[(fila["experimento"], fila["configuracion"])] = fila
    _FILAS[(experimento, configuracion)] = {"fecha": date.today().isoformat(), "seccion": seccion,
                                           "experimento": experimento, "configuracion": configuracion,
                                           "resultado": resultado, "valor": valor}
    try:
        with BITACORA.open("w", newline="", encoding="utf-8") as f:
            escritor = csv.DictWriter(f, fieldnames=_COLUMNAS)
            escritor.writeheader()
            escritor.writerows(_FILAS.values())
    except PermissionError:
        p.nota(f"No pude escribir {BITACORA}. Ciérralo si está abierto en Excel y ejecuta de nuevo.", "error")


def _leer() -> list | None:
    """Las filas de la bitácora, aunque Excel la haya guardado con punto y coma o con la codificación de Windows."""
    try:
        datos = BITACORA.read_bytes()
    except OSError:
        return None
    for codificacion in ("utf-8-sig", "cp1252"):
        try:
            contenido = datos.decode(codificacion)
            break
        except UnicodeDecodeError:
            continue
    else:
        return None
    if not contenido.strip():
        return []
    primera = contenido.splitlines()[0]
    lector = csv.DictReader(io.StringIO(contenido), delimiter=";" if primera.count(";") > primera.count(",") else ",")
    try:
        filas = list(lector)
    except csv.Error:
        return None
    if not set(_COLUMNAS) <= {c.strip().lower() for c in lector.fieldnames or []}:
        return None
    return [{k: (fila.get(k) or fila.get(k.capitalize()) or "") for k in _COLUMNAS} for fila in filas]


@amable
def mostrar_bitacora() -> None:
    """Muestra la bitácora que va en la entrega, o avisa si todavía no hay experimentos anotados."""
    if not BITACORA.exists():
        p.nota("Todavía no hay experimentos anotados. Ejecuta las secciones 2 a 5 y vuelve a esta celda.", "aviso",
               "La bitácora")
        return
    filas = _leer()
    if filas is None:
        raise ErrorDeLaboratorio(f"No pude leer {BITACORA}. Si lo abriste en Excel, ciérralo y ejecuta de nuevo un "
                                 "experimento. El notebook guarda un respaldo y escribe una bitácora nueva.")
    p.mostrar_tabla(filas, titulo=f"📄 {BITACORA.name} · {len(filas)} {'experimento' if len(filas) == 1 else 'experimentos'}")
