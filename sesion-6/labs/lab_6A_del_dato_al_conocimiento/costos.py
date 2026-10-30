"""El costo del error con el German Credit (Statlog, UCI): el umbral de decisión y la matriz de costos (Laboratorio 6A).

Un bosque aleatorio estima, para cada solicitud, la probabilidad de que sea de un mal pagador. Esa probabilidad sale de
una validación cruzada de 5 partes: cada solicitud la evalúa un bosque que no la vio. Después se decide con un umbral:
se rechaza desde esa probabilidad. Cada umbral da una matriz de confusión, y con la matriz de costos, un costo total.
"""
from __future__ import annotations

import csv
import math
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

import graficas
import presentacion as p
from arboles import SEMILLA, ErrorDeLaboratorio, _amable, _n, _pct, _sklearn

ARCHIVO = Path("datos") / "credito_aleman.csv"
NUMERICAS = ["duracion_meses", "monto_DM", "cuota_porcentaje_ingreso", "años_en_residencia", "edad",
             "creditos_en_este_banco", "personas_a_cargo"]
NOMBRES = {"saldo_cuenta_corriente": "saldo de la cuenta corriente", "duracion_meses": "duración (meses)",
           "proposito": "propósito", "monto_DM": "monto (DM)", "ahorros": "ahorros",
           "antiguedad_empleo": "antigüedad en el empleo"}


@dataclass
class Credito:
    filas: list
    malo: np.ndarray          # 1 si fue mal pagador
    probabilidad: np.ndarray  # probabilidad de ser mal pagador según un bosque que no vio la solicitud
    segundos: float


@_amable
def cargar_credito(ruta=ARCHIVO, mostrar: bool = True) -> Credito | None:
    """Lee las 1000 solicitudes y estima la probabilidad de que cada una sea de un mal pagador."""
    ruta = Path(ruta)
    if not ruta.exists():
        raise ErrorDeLaboratorio(f"No encuentro {ruta}. Abra el notebook desde la carpeta del laboratorio y reinicie el kernel.")
    _sklearn()
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import StratifiedKFold, cross_val_predict
    from sklearn.preprocessing import OneHotEncoder
    with ruta.open(encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    categoricas = [c for c in filas[0] if c not in NUMERICAS and c != "pagador"]
    numeros = np.array([[float(f[c]) for c in NUMERICAS] for f in filas])
    codificador = OneHotEncoder(sparse_output=False)
    categorias = codificador.fit_transform(np.array([[f[c] for c in categoricas] for f in filas], dtype=object))
    X = np.hstack([numeros, categorias])
    malo = np.array([1 if f["pagador"] == "malo" else 0 for f in filas])
    inicio = time.perf_counter()
    cv = StratifiedKFold(5, shuffle=True, random_state=SEMILLA)
    probabilidad = cross_val_predict(RandomForestClassifier(300, min_samples_leaf=3, random_state=SEMILLA), X, malo,
                                     cv=cv, method="predict_proba")[:, 1]
    credito = Credito(filas, malo, probabilidad, time.perf_counter() - inicio)
    if mostrar:
        p.mostrar_tabla([{**{"solicitud": i + 1}, **{nombre: f[c] for c, nombre in NOMBRES.items()}, "pagador": f["pagador"]}
                         for i, f in enumerate(filas[:6])], titulo="Seis de las 1000 solicitudes (se muestran 6 de sus 18 datos)")
        p.nota(f"{len(filas)} solicitudes; {int(malo.sum())} fueron de malos pagadores ({_pct(malo.mean(), 0)}). DM son "
               f"marcos alemanes, la moneda de Alemania antes del euro. Un bosque "
               f"aleatorio de 300 árboles estimó la probabilidad de que cada una fuera de un mal pagador, con validación "
               f"cruzada de 5 partes (tardó {'menos de 1 s' if credito.segundos < 1 else _n(credito.segundos, 1) + ' s'}).",
               "info", "Las solicitudes de crédito")
    return credito


def _validar_costo(nombre: str, valor) -> float:
    if isinstance(valor, str):
        raise ErrorDeLaboratorio(f"{nombre} es un número: escríbalo sin comillas.")
    if isinstance(valor, tuple):
        raise ErrorDeLaboratorio(f"{nombre} quedó como dos números: ¿escribió una coma decimal? Use punto, por ejemplo 2.5.")
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) or math.isnan(valor) or valor <= 0 or valor > 1000:
        raise ErrorDeLaboratorio(f"{nombre} debe ser un número mayor que 0 (y razonable, hasta 1000); escribió {valor!r}.")
    return float(valor)


def _validar_umbrales(umbrales) -> list:
    if isinstance(umbrales, tuple):
        raise ErrorDeLaboratorio("Escriba los umbrales entre corchetes y separados por comas, como [0.5, 1/6].")
    if isinstance(umbrales, (int, float)) and not isinstance(umbrales, bool):
        umbrales = [umbrales]
    if not isinstance(umbrales, list) or not umbrales:
        raise ErrorDeLaboratorio("UMBRALES debe ser una lista entre corchetes, como [0.5, 1/6].")
    if len(umbrales) > 6:
        raise ErrorDeLaboratorio("Use hasta 6 umbrales, para que las matrices quepan en la pantalla.")
    limpios = []
    for u in umbrales:
        if isinstance(u, str) and "%" in u:
            raise ErrorDeLaboratorio(f"Escriba los umbrales como fracciones, sin % ni comillas: 50 % se escribe 0.5; encontré {u!r}.")
        if isinstance(u, str):
            raise ErrorDeLaboratorio(f"El umbral {u!r} va sin comillas: escriba 0.5, o 1/6 para una fracción.")
        if isinstance(u, bool) or not isinstance(u, (int, float)) or math.isnan(u):
            raise ErrorDeLaboratorio(f"Cada umbral es un número entre 0 y 1; encontré {u!r}.")
        if not 0 < u < 1:
            if u in (0, 0.0):
                pista = " ¿Escribió una coma decimal, como 0,5? Python lo lee como dos números, 0 y 5: use 0.5."
            elif 1 < u <= 100:
                pista = f" Si es un porcentaje, divídalo por 100: {u:g} % se escribe {round(u / 100, 4):g}."
            else:
                pista = ""
            raise ErrorDeLaboratorio(f"Cada umbral debe estar entre 0 y 1, sin incluirlos; encontré {u}.{pista}")
        if u not in limpios:
            limpios.append(float(u))
    return limpios


def _decidir(credito: Credito, umbral: float, costo_mal_aprobado: float, costo_buen_rechazado: float) -> dict:
    rechaza = credito.probabilidad >= umbral
    malo = credito.malo == 1
    r = {"umbral": umbral, "malos_aprobados": int((~rechaza & malo).sum()), "malos_rechazados": int((rechaza & malo).sum()),
         "buenos_rechazados": int((rechaza & ~malo).sum()), "buenos_aprobados": int((~rechaza & ~malo).sum())}
    r["costo"] = costo_mal_aprobado * r["malos_aprobados"] + costo_buen_rechazado * r["buenos_rechazados"]
    r["exactitud"] = (r["malos_rechazados"] + r["buenos_aprobados"]) / len(credito.malo)
    return r


def _texto_umbral(u: float) -> str:
    """0.5 se muestra como 0,5; 0.1666…, como 1/6; los demás, con tres decimales."""
    if abs(u * 100 - round(u * 100)) < 1e-9:
        return _n(u, 2).rstrip("0").rstrip(",")
    for d in range(3, 21):
        if abs(u * d - 1) < 1e-9:
            return f"1/{d}"
    return _n(u, 3)


@_amable
def decidir_con_costos(credito: Credito, umbrales, costo_mal_aprobado=5, costo_buen_rechazado=1) -> list | None:
    """Compara umbrales de decisión: la matriz de confusión con su costo, el costo total y los aciertos de cada uno."""
    if credito is None:
        raise ErrorDeLaboratorio("Primero ejecute la celda que carga las solicitudes de crédito.")
    cm = _validar_costo("COSTO_MAL_APROBADO", costo_mal_aprobado)
    cb = _validar_costo("COSTO_BUEN_RECHAZADO", costo_buen_rechazado)
    lista = _validar_umbrales(umbrales)
    resultados = []
    for u in lista:
        r = _decidir(credito, u, cm, cb)
        r["nombre"] = f"umbral {_texto_umbral(u)}"
        resultados.append(r)
    graficas.matrices_costo(resultados, cm, cb)
    malos, buenos = int(credito.malo.sum()), int(len(credito.malo) - credito.malo.sum())
    referencias = {"aprobar": cm * malos, "rechazar": cb * buenos}
    tabla = [{"decisión": "Referencia: aprobar a todos", "aciertos": _pct(buenos / len(credito.malo)),
              "malos pagadores aprobados": malos, "buenos pagadores rechazados": 0, "costo total": _n(referencias["aprobar"])},
             {"decisión": "Referencia: rechazar a todos", "aciertos": _pct(malos / len(credito.malo)),
              "malos pagadores aprobados": 0, "buenos pagadores rechazados": buenos, "costo total": _n(referencias["rechazar"])}]
    tabla += [{"decisión": f"Rechazar desde una probabilidad de {_texto_umbral(r['umbral'])}", "aciertos": _pct(r["exactitud"]),
               "malos pagadores aprobados": r["malos_aprobados"], "buenos pagadores rechazados": r["buenos_rechazados"],
               "costo total": _n(r["costo"])} for r in resultados]
    p.mostrar_tabla(tabla, titulo=f"Costo con la matriz: aprobar a un mal pagador cuesta {_n(cm, 2 if not cm.is_integer() else 0)}; "
                                  f"rechazar a uno bueno, {_n(cb, 2 if not cb.is_integer() else 0)}")
    curva = [_decidir(credito, u, cm, cb) for u in np.round(np.arange(0.01, 1.0, 0.01), 2)]
    minimo = min(curva, key=lambda c: (c["costo"], abs(c["umbral"] - 0.5)))
    teorico = cb / (cb + cm)
    texto = _texto_umbral(teorico)
    texto = f"{texto} ≈ {_n(teorico, 3)}" if "/" in texto else texto
    graficas.curva_costo(curva, resultados, teorico, texto, minimo, referencias)
    return resultados
