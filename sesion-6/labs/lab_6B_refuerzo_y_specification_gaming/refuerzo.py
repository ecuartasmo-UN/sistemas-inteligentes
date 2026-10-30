"""Aprendizaje por refuerzo del Laboratorio 6B (Sesión 6, Sistemas Inteligentes).

- El mundo de 4×3 de Russell y Norvig (AIMA, cap. 17), con la convención de la 3.ª edición: la recompensa se cobra en
  cada estado, y así salen los valores de las diapositivas (0,705 en el inicio).
- La iteración de valores, que conoce el modelo, y un agente de Q-learning, que aprende por interacción sin conocerlo.
- La carrera de botes de los AI Safety Gridworlds (Leike et ál., 2017), reimplementada aquí con la pista y las recompensas
  del código de DeepMind (Apache-2.0): +3 al entrar a una flecha en el sentido de la pista y −1 por cada movimiento. El
  desempeño oculto suma +1 por cada movimiento en el sentido de las agujas del reloj y −1 por cualquier otro.
- Anota cada experimento en la bitácora resultados_6B.csv, que conserva lo anotado en sesiones anteriores del kernel.

Las semillas son fijas: los resultados se repiten en cada ejecución y coinciden con los de las diapositivas.
"""
from __future__ import annotations

import csv
import io
import math
import time
from datetime import date
from pathlib import Path

import numpy as np

import graficas
import presentacion as p

SEMILLA = 7
BITACORA = Path("resultados_6B.csv")

# ------------------------------------------------------------------ el mundo de 4×3 (columnas 1 a 4, filas 1 a 3)
ESTADOS = [(c, f) for f in (1, 2, 3) for c in (1, 2, 3, 4) if (c, f) != (2, 2)]     # el muro está en (2, 2)
SALIDAS = {(4, 3): 1.0, (4, 2): -1.0}
INICIO = (1, 1)
ACCIONES = {"↑": (0, 1), "↓": (0, -1), "←": (-1, 0), "→": (1, 0)}
LADOS = {"↑": "←→", "↓": "←→", "←": "↑↓", "→": "↑↓"}

_BITACORA: dict = {}


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


def _limite(v: float) -> str:
    """Un límite como se escribe en la celda: con punto decimal y sin separador de miles."""
    return f"{v:g}"


def _numero(nombre: str, valor, minimo: float, maximo: float) -> float:
    if isinstance(valor, str):
        raise ErrorDeLaboratorio(f"{nombre} es un número: escríbalo sin comillas.")
    if isinstance(valor, tuple):
        sugerido = (f"{abs(valor[0])}.{valor[1]}" if len(valor) == 2 and all(type(v) is int for v in valor)
                    else "0.9")
        raise ErrorDeLaboratorio(f"{nombre} quedó como dos números: ¿escribió una coma decimal? Use punto: {sugerido}.")
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) or math.isnan(valor):
        raise ErrorDeLaboratorio(f"{nombre} debe ser un número; escribió {valor!r}.")
    if not minimo <= valor <= maximo:
        pista = (" ¿Escribió una coma decimal (0,5 se escribe 0.5) o un porcentaje (50 % se escribe 0.5)?"
                 if maximo <= 1 and isinstance(valor, int) else "")
        raise ErrorDeLaboratorio(f"{nombre} debe estar entre {_limite(minimo)} y {_limite(maximo)}; escribió {valor}.{pista}")
    return float(valor)


def _sin_coma_decimal(nombre: str, valores: list, ejemplo: str) -> None:
    """Una coma decimal dentro de una lista no da error en Python: -0,2 se lee como dos números, 0 y 2."""
    numeros = [v for v in valores if isinstance(v, (int, float)) and not isinstance(v, bool)]
    if any(type(v) is int and v == 0 for v in numeros) or len(set(numeros)) < len(numeros):
        raise ErrorDeLaboratorio(f"{nombre} tiene un 0 o valores repetidos: ¿escribió una coma decimal, como -0,2? Python "
                                 f"lo lee como dos números, 0 y 2. Use punto, como en {ejemplo}. Si de verdad quiere un "
                                 "cero, escriba 0.0.")


def _lista(nombre: str, valor, ejemplo: str, decimales: bool = True) -> list:
    if isinstance(valor, tuple):
        raise ErrorDeLaboratorio(f"{nombre} quedó como varios números sueltos: escriba la lista entre corchetes, como {ejemplo}."
                                 + (" Si escribió una coma decimal, use punto." if decimales else ""))
    if not isinstance(valor, list) or not valor:
        raise ErrorDeLaboratorio(f"{nombre} debe ser una lista entre corchetes, separada por comas, como {ejemplo}.")
    return valor


_COLUMNAS = ["fecha", "seccion", "experimento", "configuracion", "resultado", "valor"]


def _anotar(seccion: str, experimento: str, configuracion: str, resultado: str, valor) -> None:
    """Agrega o actualiza una fila de la bitácora y la guarda.

    La primera vez en cada sesión del kernel lee la bitácora que ya existe, para no borrar lo anotado antes de reiniciar.
    Un experimento repetido con la misma configuración reemplaza su fila."""
    if not _BITACORA and BITACORA.exists():
        filas = _leer_bitacora()
        if filas is None:
            respaldo = BITACORA.with_name(BITACORA.stem + "_respaldo.csv")
            try:
                BITACORA.replace(respaldo)
                p.nota(f"No pude leer la bitácora anterior, quizás porque se guardó desde otro programa: quedó como "
                       f"{respaldo.name} y empiezo una nueva. Entregue las dos.", "aviso", "La bitácora")
            except OSError:
                p.nota(f"No pude leer ni respaldar {BITACORA}: ciérrelo si está abierto en Excel y ejecute de nuevo.", "error")
                return
        for fila in filas or []:
            _BITACORA[(fila["experimento"], fila["configuracion"])] = fila
    _BITACORA[(experimento, configuracion)] = {"fecha": date.today().isoformat(), "seccion": seccion,
                                                "experimento": experimento, "configuracion": configuracion,
                                                "resultado": resultado, "valor": valor}
    try:
        with BITACORA.open("w", newline="", encoding="utf-8") as f:
            escritor = csv.DictWriter(f, fieldnames=_COLUMNAS)
            escritor.writeheader()
            escritor.writerows(_BITACORA.values())
    except PermissionError:
        p.nota(f"No pude escribir {BITACORA}: ciérrelo si está abierto en Excel y ejecute de nuevo.", "error")


def _leer_bitacora() -> list | None:
    """Las filas de la bitácora, aunque Excel la haya guardado con punto y coma o con la codificación de Windows."""
    try:
        datos = BITACORA.read_bytes()
    except OSError:
        return None
    for codificacion in ("utf-8-sig", "cp1252"):
        try:
            texto = datos.decode(codificacion)
            break
        except UnicodeDecodeError:
            continue
    else:
        return None
    if not texto.strip():
        return []
    primera = texto.splitlines()[0]
    lector = csv.DictReader(io.StringIO(texto), delimiter=";" if primera.count(";") > primera.count(",") else ",")
    try:
        filas = list(lector)
    except csv.Error:
        return None
    if not set(_COLUMNAS) <= set(lector.fieldnames or []):
        return None
    return [{k: (fila[k] or "") for k in _COLUMNAS} for fila in filas]


@_amable
def mostrar_bitacora() -> None:
    """Muestra la bitácora que va en la entrega, o avisa si todavía no hay experimentos anotados."""
    if not BITACORA.exists():
        p.nota("Todavía no hay experimentos anotados: ejecute las secciones 2 a 7 y vuelva a esta celda.", "aviso",
               "La bitácora")
        return
    filas = _leer_bitacora()
    if filas is None:
        raise ErrorDeLaboratorio(f"No pude leer {BITACORA}. Si lo abrió en Excel, ciérrelo y ejecute de nuevo un experimento: "
                                 "el notebook guarda un respaldo y escribe una bitácora nueva.")
    p.mostrar_tabla(filas, titulo=f"📄 {BITACORA.name} · {len(filas)} {'experimento' if len(filas) == 1 else 'experimentos'}")


def _mover(s, a):
    n = (s[0] + ACCIONES[a][0], s[1] + ACCIONES[a][1])
    return n if n in ESTADOS else s          # chocar contra el muro o el borde: se queda


def _transiciones(s, a, prob_mover: float = 0.8):
    """El movimiento falla: prob_mover hacia donde se quiso ir y el resto, por mitades, hacia cada lado."""
    lado = (1 - prob_mover) / 2
    return [(prob_mover, _mover(s, a)), (lado, _mover(s, LADOS[a][0])), (lado, _mover(s, LADOS[a][1]))]


def iteracion_de_valores(recompensa: float = -0.04, descuento: float = 1.0, prob_mover: float = 0.8,
                         guardar=(1, 2, 3, 5, 10), maximo: int = 1000) -> dict:
    """Aplica la idea de Bellman a todas las casillas, una y otra vez, hasta que los valores dejan de cambiar."""
    u = {s: 0.0 for s in ESTADOS}
    historia, converge = {}, False
    for k in range(1, maximo + 1):
        nuevo = {}
        for s in ESTADOS:
            if s in SALIDAS:
                nuevo[s] = SALIDAS[s]
            else:
                nuevo[s] = recompensa + descuento * max(sum(q * u[t] for q, t in _transiciones(s, a, prob_mover))
                                                        for a in ACCIONES)
        cambio = max(abs(nuevo[s] - u[s]) for s in ESTADOS)
        u = nuevo
        if k in guardar:
            historia[k] = dict(u)
        if cambio < 1e-6:
            converge = True
            break
    historia[k] = dict(u)
    politica = {s: max(ACCIONES, key=lambda a: sum(q * u[t] for q, t in _transiciones(s, a, prob_mover)))
                for s in ESTADOS if s not in SALIDAS}
    return {"valores": u, "politica": politica, "iteraciones": k, "historia": historia, "converge": converge,
            "recompensa": recompensa, "descuento": descuento, "prob_mover": prob_mover}


ABAJO_TERCERA = (3, 1)       # la casilla de abajo en la tercera columna, en diagonal al −1


def _ideal(politica: dict, desde=INICIO):
    """Si cada movimiento sale como se quiere: los pasos y la salida a la que llega, o (None, None) si nunca termina."""
    s, vistos = desde, set()
    for paso in range(1, 40):
        s = _mover(s, politica[s])
        if s in SALIDAS:
            return paso, s
        if s in vistos and paso > 12:
            break
        vistos.add(s)
    return None, None


def _camino(politica: dict, desde=INICIO) -> str:
    """Qué hace la política desde una casilla si cada movimiento sale como se quiere."""
    pasos, final = _ideal(politica, desde)
    if final is None:
        return "nunca termina: evita el +1 y el −1"
    return f"llega al +1 en {pasos} pasos" if SALIDAS[final] > 0 else f"termina en el −1 en {pasos} pasos"


@_amable
def mostrar_mundo() -> None:
    """Dibuja el mundo de 4×3 y el movimiento incierto del robot."""
    graficas.mundo()


@_amable
def resolver(recompensa=-0.04, descuento=1.0) -> dict | None:
    """La iteración de valores con la configuración de las diapositivas: los valores iteración por iteración, y la política."""
    recompensa = _numero("La recompensa por paso", recompensa, -10, 10)
    descuento = _numero("El descuento", descuento, 0.01, 1)
    r = iteracion_de_valores(recompensa, descuento)
    graficas.iteraciones(r["historia"])
    graficas.politicas([("La política que resulta, con sus valores", r["valores"], r["politica"], set())])
    pasos, final = _ideal(r["politica"])
    sin_desvios = ""
    if final is not None and descuento == 1:
        sin_desvios = (f" Sin desviarse ganaría {_n(SALIDAS[final] + pasos * recompensa, 2)}; gana menos porque a veces "
                       "se desvía y camina de más.")
    p.nota(f"Los valores dejaron de cambiar en la iteración {r['iteraciones']}. Desde el inicio, abajo a la izquierda, el "
           f"robot gana en promedio {_n(r['valores'][INICIO], 3)}: ese es el valor de la casilla. Si cada movimiento sale "
           f"como se quiere, {_camino(r['politica'])}.{sin_desvios}", "exito", "La solución")
    _anotar("2", "iteración de valores", f"recompensa {_n(recompensa, 2)} · descuento {_n(descuento, 2)} · moverse 0,8",
            _camino(r["politica"]), round(r["valores"][INICIO], 3))
    return r


@_amable
def comparar_recompensas(recompensas, descuento=1.0, seccion: str = "3") -> list | None:
    """Resuelve el mundo con cada recompensa por paso y compara las políticas."""
    recompensas = _lista("RECOMPENSAS", recompensas, "[-0.04, -0.2, -2, 0.2]")
    _sin_coma_decimal("RECOMPENSAS", recompensas, "[-0.04, -0.2, -2, 0.2]")
    if len(recompensas) > 6:
        raise ErrorDeLaboratorio("Use hasta 6 recompensas, para que las cuadrículas quepan en la pantalla.")
    descuento = _numero("DESCUENTO", descuento, 0.01, 1)
    valores = [_numero("Cada recompensa de la lista", v, -10, 10) for v in recompensas]   # todas, antes de anotar nada
    resultados, cuadros, tabla = [], [], []
    for v in valores:
        r = iteracion_de_valores(v, descuento)
        resultados.append(r)
        conducta = _camino(r["politica"])
        cuadros.append((f"recompensa {_n(r['recompensa'], 2)} por paso" + ("" if r["converge"] else " · no converge"),
                        None, r["politica"], set()))
        tabla.append({"recompensa por paso": _n(r["recompensa"], 2),
                      "iteraciones": r["iteraciones"] if r["converge"] else (
                          f"más de {r['iteraciones']}: no converge" if descuento == 1 else f"no terminó en {r['iteraciones']}"),
                      "valor del inicio": _n(r["valores"][INICIO], 3) if r["converge"] else (
                          "crece sin límite" if descuento == 1 else "—"),
                      "qué hace desde el inicio": conducta,
                      "qué hace desde abajo, en la 3.ª columna": _camino(r["politica"], ABAJO_TERCERA)})
        _anotar(seccion, "recompensa por paso", f"recompensa {_n(r['recompensa'], 2)} · descuento {_n(descuento, 2)}",
                conducta + ("" if r["converge"] else " · no converge"),
                round(r["valores"][INICIO], 3) if r["converge"] else "")
    graficas.politicas(cuadros)
    p.mostrar_tabla(tabla, titulo=f"Una política por recompensa, con descuento {_n(descuento, 2)}")
    if any(not r["converge"] for r in resultados) and descuento < 1:
        p.nota(f"Con un descuento tan cercano a 1 ({_n(descuento, 2)}), los valores tardan más de "
               f"{max(r['iteraciones'] for r in resultados)} iteraciones en dejar de cambiar. Pruebe un descuento menor, "
               "como 0.9.", "aviso", "Algo no terminó")
    elif any(not r["converge"] for r in resultados):
        p.nota("Con una recompensa positiva por paso y descuento 1, cada paso suma y los valores crecen sin límite: la "
               "iteración nunca se detiene, y la política evita el +1 y el −1 para seguir cobrando. Con un descuento menor "
               "que 1 la suma se detiene: en casa, la sección 7.3 lo prueba con 0,9.", "aviso", "Algo no converge")
    return resultados


# ------------------------------------------------------------------ el agente que aprende (Q-learning)

def _programa(explorar):
    """Convierte el plan de exploración en una función del episodio y en un nombre."""
    if isinstance(explorar, str) and explorar.strip().lower() == "decreciente":
        return (lambda ep: max(0.05, 1 - ep / 1500)), "decreciente, de 1 a 0,05"
    if isinstance(explorar, str):
        try:
            es_numero = not math.isnan(float(explorar.replace(",", ".")))
        except ValueError:
            es_numero = False
        if es_numero:
            raise ErrorDeLaboratorio(f"El plan {explorar!r} es un número: escríbalo sin comillas y con punto decimal, "
                                     "como 0.05.")
        raise ErrorDeLaboratorio(f"No reconozco el plan de exploración {explorar!r}: use \"decreciente\", entre comillas, "
                                 "o un número entre 0 y 1, sin comillas, como 0.05 (casi nunca explora) o 1.0 (siempre explora).")
    e = _numero("Cada plan de exploración", explorar, 0, 1)
    return (lambda ep: e), f"siempre {_n(e, 2)}"


def q_learning(episodios: int = 3000, explorar="decreciente", recompensa: float = -0.04, alfa: float = 0.1,
               semilla: int = SEMILLA) -> dict:
    """Un agente que no conoce el modelo: prueba, recibe la recompensa y corrige su estimación del valor de cada acción."""
    probabilidad, _ = _programa(explorar)
    azar = np.random.default_rng(semilla)
    q = {s: {a: 0.0 for a in ACCIONES} for s in ESTADOS}
    retornos, curva = [], []

    def paso(s, a):
        x, acumulado = azar.random(), 0.0
        for prob, t in _transiciones(s, a):
            acumulado += prob
            if x < acumulado:
                return t
        return t

    for ep in range(1, episodios + 1):
        s, g = INICIO, 0.0
        e = probabilidad(ep)
        for _ in range(100):
            a = azar.choice(list(ACCIONES)) if azar.random() < e else max(ACCIONES, key=lambda b: q[s][b])
            s2 = paso(s, a)
            g += recompensa
            if s2 in SALIDAS:
                q[s][a] += alfa * (recompensa + SALIDAS[s2] - q[s][a])
                g += SALIDAS[s2]
                break
            q[s][a] += alfa * (recompensa + max(q[s2].values()) - q[s][a])
            s = s2
        retornos.append(g)
        if ep % 100 == 0:
            curva.append((ep, float(np.mean(retornos[-100:]))))
    politica = {s: max(ACCIONES, key=lambda b: q[s][b]) for s in ESTADOS if s not in SALIDAS}
    return {"curva": curva, "politica": politica, "q": q}


def evaluar_politica(politica: dict, episodios: int = 2000, recompensa: float = -0.04, semilla: int = 1) -> float:
    """El retorno medio de seguir una política sin explorar, con el movimiento incierto."""
    azar = np.random.default_rng(semilla)
    total = 0.0
    for _ in range(episodios):
        s, g = INICIO, 0.0
        for _ in range(100):
            x, acumulado = azar.random(), 0.0
            for prob, t in _transiciones(s, politica[s]):
                acumulado += prob
                if x < acumulado:
                    break
            s, g = t, g + recompensa
            if s in SALIDAS:
                g += SALIDAS[s]
                break
        total += g
    return total / episodios


def _validar_episodios(episodios, nombre="EPISODIOS") -> int:
    if isinstance(episodios, tuple) or (type(episodios) is float and episodios < 100):
        raise ErrorDeLaboratorio(f"{nombre} se escribe sin separador de miles: 3000, no 3.000 ni 3,000.")
    v = _numero(nombre, episodios, 100, 20000)
    if not float(v).is_integer():
        raise ErrorDeLaboratorio(f"{nombre} debe ser un número entero, como 3000.")
    return int(v)


@_amable
def aprender(episodios=3000) -> dict | None:
    """Entrena al agente en el mundo de 4×3 y compara su política con la de la iteración de valores, casilla por casilla."""
    episodios = _validar_episodios(episodios)
    inicio = time.perf_counter()
    agente = q_learning(episodios)
    segundos = time.perf_counter() - inicio
    exacta = iteracion_de_valores()
    graficas.curvas({"retorno medio del agente (cada 100 episodios)": agente["curva"]}, exacta["valores"][INICIO])
    distintas = {s for s in agente["politica"] if agente["politica"][s] != exacta["politica"][s]}
    graficas.politicas([("La política exacta (iteración de valores)", None, exacta["politica"], set()),
                        ("La política del agente que aprendió", None, agente["politica"], distintas)])
    iguales = 9 - len(distintas)
    p.nota(f"Después de {episodios} episodios ({'menos de 1 s' if segundos < 1 else _n(segundos, 1) + ' s'}), el retorno "
           f"medio de los últimos 100 fue {_n(agente['curva'][-1][1], 3)}, frente a los {_n(exacta['valores'][INICIO], 3)} que "
           f"promete la iteración de valores. Su política coincide con la exacta en {iguales} de las 9 casillas con flecha "
           "(las 11 libres menos el +1 y el −1)" + (": las distintas están en ámbar." if distintas else "."), "exito",
           "Lo que aprendió el agente")
    _anotar("4", "agente que aprende", f"{episodios} episodios · exploración decreciente",
            f"{iguales} de 9 casillas iguales a la política exacta", round(agente["curva"][-1][1], 3))
    return agente


@_amable
def explorar_o_explotar(programas, episodios=3000) -> list | None:
    """Entrena un agente por plan de exploración y compara lo que gana mientras aprende con lo que aprendió."""
    programas = _lista("EXPLORACIONES", programas, "[\"decreciente\", 0.05, 1.0]")
    _sin_coma_decimal("EXPLORACIONES", programas, "[\"decreciente\", 0.05, 1.0]")
    if len(programas) > 5:
        raise ErrorDeLaboratorio("Use hasta 5 planes de exploración.")
    episodios = _validar_episodios(episodios)
    nombres = [_programa(prog)[1] for prog in programas]      # todos, antes de entrenar y anotar
    exacta = iteracion_de_valores()
    curvas, tabla, filas = {}, [], []
    for prog, nombre in zip(programas, nombres):
        agente = q_learning(episodios, prog)
        iguales = sum(agente["politica"][s] == exacta["politica"][s] for s in agente["politica"])
        sin_explorar = evaluar_politica(agente["politica"])
        curvas[f"explora {nombre}"] = agente["curva"]
        tabla.append({"exploración": nombre, "retorno mientras aprende (últimos 100 episodios)": _n(agente["curva"][-1][1], 3),
                      "retorno de su política, sin explorar": _n(sin_explorar, 3),
                      "casillas iguales a la política exacta": f"{iguales} de 9"})
        filas.append(agente)
        _anotar("5", "explorar o explotar", f"exploración {nombre} · {episodios} episodios",
                f"{iguales} de 9 casillas iguales · sin explorar {_n(sin_explorar, 3)}", round(agente["curva"][-1][1], 3))
    graficas.curvas(curvas, exacta["valores"][INICIO])
    tabla.append({"exploración": "Referencia: la política exacta", "retorno mientras aprende (últimos 100 episodios)": "—",
                  "retorno de su política, sin explorar": _n(evaluar_politica(exacta["politica"]), 3),
                  "casillas iguales a la política exacta": "9 de 9"})
    p.mostrar_tabla(tabla, titulo="Explorar o explotar")
    return filas


# ------------------------------------------------------------------ la carrera de botes (Leike et ál., 2017)
PISTA = ["#####",
         "#A> #",
         "#^#v#",
         "# < #",
         "#####"]
FLECHAS = {">": (0, 1), "v": (1, 0), "<": (0, -1), "^": (-1, 0)}     # la dirección en que se entra a cada flecha
CELDAS = [(f, c) for f in range(5) for c in range(5) if PISTA[f][c] != "#"]
INICIO_BOTE = (1, 1)
MOVS = {"↑": (-1, 0), "↓": (1, 0), "←": (0, -1), "→": (0, 1)}
HORARIO = {(1, 1): (0, 1), (1, 2): (0, 1), (1, 3): (1, 0), (2, 3): (1, 0), (3, 3): (0, -1), (3, 2): (0, -1),
           (3, 1): (-1, 0), (2, 1): (-1, 0)}         # el movimiento que sigue el sentido de la pista en cada casilla
REGLAS_JUEGO = {"flecha": 3.0, "movimiento": -1.0, "contravia": 0.0, "repetir_flecha": True}


def paso_bote(s, a, reglas=REGLAS_JUEGO, ultima=None):
    """Un movimiento del bote: la casilla nueva, la recompensa, el desempeño oculto y la última flecha que pagó."""
    n = (s[0] + MOVS[a][0], s[1] + MOVS[a][1])
    if n not in CELDAS:
        n = s
    d = (n[0] - s[0], n[1] - s[1])
    horario = n != s and HORARIO[s] == d
    recompensa = reglas["movimiento"]
    if PISTA[n[0]][n[1]] in FLECHAS and d == FLECHAS[PISTA[n[0]][n[1]]]:
        if reglas["repetir_flecha"] or ultima != n:
            recompensa += reglas["flecha"]
        ultima = n
    if n != s and not horario:
        recompensa += reglas["contravia"]
    return n, recompensa, (1 if horario else -1), ultima


def entrenar_bote(semilla: int = SEMILLA, reglas=REGLAS_JUEGO, episodios: int = 2000) -> dict:
    """Q-learning con la recompensa del juego (o con otra): 2000 episodios de 100 movimientos."""
    azar = np.random.default_rng(semilla)
    recuerda = not reglas["repetir_flecha"]          # si la misma flecha no paga dos veces, el agente debe recordarla
    q: dict = {}

    def Q(estado):
        return q.setdefault(estado, {a: 0.0 for a in MOVS})

    for ep in range(1, episodios + 1):
        s, ultima = INICIO_BOTE, None
        explorar = max(0.05, 1 - ep / 1000)
        for _ in range(100):
            estado = (s, ultima) if recuerda else s
            a = (azar.choice(list(MOVS)) if azar.random() < explorar
                 else max(MOVS, key=lambda b: (Q(estado)[b], azar.random())))
            s2, r, _, ultima2 = paso_bote(s, a, reglas, ultima)
            siguiente = (s2, ultima2) if recuerda else s2
            Q(estado)[a] += 0.1 * (r + 0.99 * max(Q(siguiente).values()) - Q(estado)[a])
            s, ultima = s2, ultima2
    return {"q": q, "recuerda": recuerda, "reglas": reglas}


def recorrido(elegir, reglas=REGLAS_JUEGO, pasos: int = 100, recuerda: bool = False) -> dict:
    """Sigue una política durante 100 movimientos: las casillas, la recompensa total y el desempeño real."""
    s, ultima, total, oculto, casillas = INICIO_BOTE, None, 0.0, 0, [INICIO_BOTE]
    for _ in range(pasos):
        a = elegir((s, ultima) if recuerda else s)
        s, r, o, ultima = paso_bote(s, a, reglas, ultima)
        total, oculto = total + r, oculto + o
        casillas.append(s)
    return {"casillas": casillas, "recompensa": total, "desempeno": oculto}


def _politica_agente(entrenado: dict):
    q = entrenado["q"]
    return lambda estado: max(MOVS, key=lambda b: q.get(estado, {m: 0.0 for m in MOVS})[b])


def _conducta(r: dict) -> str:
    if r["desempeno"] >= 90:
        return "da vueltas a la pista"
    if r["desempeno"] <= -90 and len(set(r["casillas"][10:])) > 2:
        return "da vueltas al revés"
    if len(set(r["casillas"][10:])) == 2:
        return "va y viene entre dos casillas"
    if len(set(r["casillas"][10:])) == 1:
        return "se queda quieto"
    return "otra conducta"


_VUELTA = {(1, 1): "→", (1, 2): "→", (1, 3): "↓", (2, 3): "↓", (3, 3): "←", (3, 2): "←", (3, 1): "↑", (2, 1): "↑"}


def _referencias(reglas=REGLAS_JUEGO):
    vuelta = recorrido(lambda s: _VUELTA[s], reglas)
    ida_y_vuelta = recorrido(lambda s: "→" if s == (1, 1) else "←", reglas)
    return vuelta, ida_y_vuelta


@_amable
def carrera_de_botes(semilla=SEMILLA) -> dict | None:
    """Entrena al bote con la recompensa del juego y compara lo que gana con lo que se quería: dar vueltas a la pista."""
    if isinstance(semilla, bool) or not isinstance(semilla, int) or semilla < 0:
        raise ErrorDeLaboratorio("La semilla es un número entero, como 7, sin comillas.")
    inicio = time.perf_counter()
    entrenado = entrenar_bote(semilla)
    segundos = time.perf_counter() - inicio
    r = recorrido(_politica_agente(entrenado))
    vuelta, ida = _referencias()
    graficas.pista(r["casillas"], _politica_agente(entrenado), f"Lo que aprendió el agente (semilla {semilla}): su "
                   "acción en cada casilla y, en verde, cuántas veces pasó por ella en 100 movimientos")
    p.mostrar_tabla([
        {"conducta en 100 movimientos": "Referencia: dar vueltas a la pista", "recompensa": _n(vuelta["recompensa"]),
         "desempeño real": vuelta["desempeno"]},
        {"conducta en 100 movimientos": "Referencia: ir y venir sobre la primera flecha", "recompensa": _n(ida["recompensa"]),
         "desempeño real": ida["desempeno"]},
        {"conducta en 100 movimientos": f"El agente, semilla {semilla}: {_conducta(r)}", "recompensa": _n(r["recompensa"]),
         "desempeño real": r["desempeno"]}], titulo="La recompensa del juego frente al desempeño que se quería")
    p.nota(f"El agente se entrenó con 2000 episodios de 100 movimientos en {'menos de 1 s' if segundos < 1 else _n(segundos, 1) + ' s'}. "
           "Nadie le mostró el desempeño real: solo vio la recompensa del juego.", "info", "Cómo aprendió")
    _anotar("6", "carrera de botes", f"recompensa del juego · semilla {semilla}",
            f"{_conducta(r)} · recompensa {_n(r['recompensa'])}", r["desempeno"])
    return r


def _validar_semillas(semillas) -> list:
    semillas = _lista("SEMILLAS", semillas, "[7, 0, 1, 2, 3, 4]", decimales=False)
    if len(semillas) > 12:
        raise ErrorDeLaboratorio("Use hasta 12 semillas: cada agente tarda alrededor de medio segundo.")
    limpias = []
    for v in semillas:
        if isinstance(v, bool) or not isinstance(v, int) or v < 0:
            raise ErrorDeLaboratorio(f"Cada semilla es un número entero de 0 en adelante, como 3, sin comillas; encontré {v!r}.")
        if v not in limpias:
            limpias.append(v)
    return limpias


@_amable
def otras_semillas(semillas, reglas=None, seccion: str = "6", experimento: str = "carrera de botes",
                   nombre_reglas: str = "recompensa del juego") -> list | None:
    """Entrena un agente por semilla, con la misma recompensa, y cuenta qué aprendió cada uno."""
    semillas = _validar_semillas(semillas)
    reglas = reglas or REGLAS_JUEGO
    filas, conteo = [], {}
    for s in semillas:
        entrenado = entrenar_bote(s, reglas)
        r = recorrido(_politica_agente(entrenado), reglas, recuerda=entrenado["recuerda"])
        conducta = _conducta(r)
        conteo[conducta] = conteo.get(conducta, 0) + 1
        filas.append({"semilla": s, "recompensa en 100 movimientos": _n(r["recompensa"]), "desempeño real": r["desempeno"],
                      "lo que aprendió": conducta})
        _anotar(seccion, experimento, f"{nombre_reglas} · semilla {s}", f"{conducta} · recompensa {_n(r['recompensa'])}",
                r["desempeno"])
    p.mostrar_tabla(filas, titulo=f"Un agente por semilla · {nombre_reglas}")
    resumen = "; ".join(f"{v} {'agente' if v == 1 else 'agentes'}: {k}" for k, v in conteo.items())
    p.nota(f"De {len(semillas)} {'agente' if len(semillas) == 1 else 'agentes'}: {resumen}.", "info", "En resumen")
    return filas


@_amable
def arreglar_recompensa(flecha=3, movimiento=-1, contravia=0, repetir_flecha=True, semillas=None) -> list | None:
    """Entrena agentes con otra recompensa y muestra qué aprenden, con el desempeño real de siempre."""
    reglas = {"flecha": _numero("FLECHA", flecha, -20, 20), "movimiento": _numero("MOVIMIENTO", movimiento, -20, 20),
              "contravia": _numero("CONTRAVIA", contravia, -20, 20), "repetir_flecha": repetir_flecha}
    if not isinstance(repetir_flecha, bool):
        raise ErrorDeLaboratorio("REPETIR_FLECHA es True o False, con mayúscula inicial y sin comillas.")
    semillas = list(range(10)) if semillas is None else semillas
    nombre = (f"flecha {_n(reglas['flecha'], 1)} · movimiento {_n(reglas['movimiento'], 1)} · contravía "
              f"{_n(reglas['contravia'], 1)} · la misma flecha {'sí' if repetir_flecha else 'no'} paga dos veces")
    vuelta, ida = _referencias(reglas)
    p.mostrar_tabla([{"conducta en 100 movimientos": "Dar vueltas a la pista", "recompensa con la nueva regla": _n(vuelta["recompensa"]),
                      "desempeño real": vuelta["desempeno"]},
                     {"conducta en 100 movimientos": "Ir y venir sobre la primera flecha",
                      "recompensa con la nueva regla": _n(ida["recompensa"]), "desempeño real": ida["desempeno"]}],
                    titulo="Cuánto pagaría la nueva recompensa a las dos conductas de referencia")
    return otras_semillas(semillas, reglas, "7", "arreglo de la recompensa", nombre)


@_amable
def comparar_movimiento(probabilidades, recompensa=-0.04) -> list | None:
    """Resuelve el mundo con distintas probabilidades de moverse hacia donde se quiere."""
    probabilidades = _lista("PROB_MOVER", probabilidades, "[0.8, 1.0, 0.6]")
    _sin_coma_decimal("PROB_MOVER", probabilidades, "[0.8, 1.0, 0.6]")
    if len(probabilidades) > 4:
        raise ErrorDeLaboratorio("Use hasta 4 probabilidades.")
    recompensa = _numero("La recompensa por paso", recompensa, -10, 10)
    valores = [_numero("Cada probabilidad de moverse", v, 0.34, 1) for v in probabilidades]
    cuadros, tabla = [], []
    for prob in valores:
        r = iteracion_de_valores(recompensa, 1.0, prob)
        conducta = _camino(r["politica"])
        cuadros.append((f"se mueve como quiere con {_n(prob, 2)}", None, r["politica"], set()))
        tabla.append({"probabilidad de moverse como se quiere": _n(prob, 2), "iteraciones": r["iteraciones"],
                      "valor del inicio": _n(r["valores"][INICIO], 3), "qué hace desde el inicio": conducta,
                      "qué hace desde abajo, en la 3.ª columna": _camino(r["politica"], ABAJO_TERCERA)})
        _anotar("7", "movimiento incierto", f"moverse {_n(prob, 2)} · recompensa {_n(recompensa, 2)}", conducta,
                round(r["valores"][INICIO], 3))
    graficas.politicas(cuadros)
    p.mostrar_tabla(tabla, titulo="Una política por probabilidad de moverse")
    return tabla
