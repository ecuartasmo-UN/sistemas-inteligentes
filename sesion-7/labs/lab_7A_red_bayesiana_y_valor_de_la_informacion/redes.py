"""La tasa base y la red de la alarma del Laboratorio 7A (Sesión 7, Sistemas Inteligentes).

- La alarma de vibración de MantenIA: la regla de Bayes con frecuencias naturales (Gigerenzer y Hoffrage, 1995).
  MantenIA es una empresa ficticia, y sus cifras son ilustrativas.
- La red de la alarma de Pearl (1988), con las tablas de Russell y Norvig, AIMA, 4.ª ed., fig. 13.2.
  pyAgrum calcula cada consulta. El módulo repite la cuenta a mano, sumando las 32 combinaciones, y avisa si no coinciden.
- Cada consulta se anota en la bitácora resultados_7A.csv.
"""
from __future__ import annotations

import itertools
import unicodedata

import pyagrum as gum

import apoyo as a
import graficas as g
import presentacion as p
from apoyo import ErrorDeLaboratorio, amable

# Las tablas de AIMA: la probabilidad de «sí» de cada nodo, según sus padres
TABLAS = {
    "Robo": 0.001,
    "Sismo": 0.002,
    "Alarma": {("si", "si"): 0.95, ("si", "no"): 0.94, ("no", "si"): 0.29, ("no", "no"): 0.001},   # (robo, sismo)
    "Juan": {"si": 0.90, "no": 0.05},     # según la alarma
    "María": {"si": 0.70, "no": 0.01},    # según la alarma
}
NODOS = ["Robo", "Sismo", "Alarma", "Juan", "María"]
_INTERNO = {"Robo": "Robo", "Sismo": "Sismo", "Alarma": "Alarma", "Juan": "Juan", "María": "Maria"}


def _sin_tildes(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn").lower().strip()


_NOMBRES = {_sin_tildes(n): n for n in NODOS}


# ----------------------------------------------------------------------------- 1. la tasa base

@amable
def tasa_base(tasas, sensibilidad=0.95, especificidad=0.95, bombas: int = 1000) -> list | None:
    """La alarma de vibración con frecuencias naturales: de los avisos, ¿cuántos son fallas de verdad?"""
    tasas = a.lista_de_probabilidades("TASAS_FALLA", tasas, "[0.02, 0.10]", aviso_uno=True)
    sens = a.probabilidad("SENSIBILIDAD", sensibilidad)
    esp = a.probabilidad("ESPECIFICIDAD", especificidad)
    # Frecuencias naturales: se cuentan bombas enteras. Si 1 000 no alcanza, se cuentan 10 000 o 100 000
    for bombas in (bombas, bombas * 10, bombas * 100):
        conteos = [bombas * t * f for t in tasas for f in (sens, 1 - sens)]
        conteos += [bombas * (1 - t) * f for t in tasas for f in (esp, 1 - esp)]
        if all(abs(c - round(c)) < 1e-6 for c in conteos):
            break
    filas = []
    for tasa in tasas:
        fallan = bombas * tasa
        sanas = bombas - fallan
        detectadas = fallan * sens
        falsas = sanas * (1 - esp)
        avisos = detectadas + falsas
        posterior = detectadas / avisos if avisos else 0.0
        filas.append({"Tasa de falla": a.pct(tasa), "Fallan": a.num(fallan, 1), "Sanas": a.num(sanas, 1),
                      "Avisos verdaderos": a.num(detectadas, 1), "Falsas alarmas": a.num(falsas, 1),
                      "Avisos en total": a.num(avisos, 1), "P(falla | aviso)": a.pct(posterior)})
        a.anotar("1", "tasa base", f"tasa {a.num(tasa, 4)}, sensibilidad {a.num(sens, 4)}, especificidad {a.num(esp, 4)}",
                 "P(falla | aviso)", round(posterior, 4))
    primera = tasas[0]
    g.arbol_de_frecuencias(bombas, primera, sens, esp)
    filas.append({"Tasa de falla": "creerle siempre a la alarma", "Fallan": "", "Sanas": "", "Avisos verdaderos": "",
                  "Falsas alarmas": "", "Avisos en total": "", "P(falla | aviso)": a.pct(sens)})
    p.mostrar_tabla(filas, titulo=f"De {a.num(bombas)} bombas: ¿cuántos avisos son fallas de verdad?",
                    referencia={len(filas) - 1},
                    pie="La última fila es la referencia: confundir la sensibilidad de la alarma con P(falla | aviso).")
    if len(tasas) == 1:
        p.nota("Agrega otras tasas de falla a la lista, como 0.10 y 0.30, para ver cómo cambia P(falla | aviso).", "info")
    return filas


# ----------------------------------------------------------------------------- 2. la red de la alarma

def _revisar_tablas(tablas: dict) -> dict:
    """Revisa que cada número de las tablas sea una probabilidad."""
    t = {"Robo": a.probabilidad("P(robo)", tablas["Robo"]), "Sismo": a.probabilidad("P(sismo)", tablas["Sismo"])}
    t["Alarma"] = {k: a.probabilidad(f"P(alarma | robo = {k[0]}, sismo = {k[1]})", v) for k, v in tablas["Alarma"].items()}
    t["Juan"] = {k: a.probabilidad(f"P(Juan llama | alarma = {k})", v) for k, v in tablas["Juan"].items()}
    t["María"] = {k: a.probabilidad(f"P(María llama | alarma = {k})", v) for k, v in tablas["María"].items()}
    return t


def construir(tablas: dict = TABLAS) -> gum.BayesNet:
    """Arma la red con sus cinco tablas, siempre de forma explícita."""
    bn = gum.fastBN("Robo{no|si}->Alarma{no|si}<-Sismo{no|si};Alarma->Juan{no|si};Alarma->Maria{no|si}")
    bn.cpt("Robo").fillWith([1 - tablas["Robo"], tablas["Robo"]])
    bn.cpt("Sismo").fillWith([1 - tablas["Sismo"], tablas["Sismo"]])
    for (robo, sismo), q in tablas["Alarma"].items():
        bn.cpt("Alarma")[{"Robo": robo, "Sismo": sismo}] = [1 - q, q]
    for alarma in ("si", "no"):
        bn.cpt("Juan")[{"Alarma": alarma}] = [1 - tablas["Juan"][alarma], tablas["Juan"][alarma]]
        bn.cpt("Maria")[{"Alarma": alarma}] = [1 - tablas["María"][alarma], tablas["María"][alarma]]
    return bn


def _conjunta(tablas: dict, r: str, s: str, al: str, j: str, m: str) -> float:
    """La probabilidad de una combinación: el producto de las cinco tablas (la factorización de la red)."""
    def si_no(q, valor):
        return q if valor == "si" else 1 - q
    return (si_no(tablas["Robo"], r) * si_no(tablas["Sismo"], s) * si_no(tablas["Alarma"][(r, s)], al)
            * si_no(tablas["Juan"][al], j) * si_no(tablas["María"][al], m))


def a_mano(tablas: dict, evidencia: dict) -> dict | None:
    """La probabilidad de «sí» de cada nodo dada la evidencia, sumando las 32 combinaciones."""
    total, si = 0.0, dict.fromkeys(NODOS, 0.0)
    for combinacion in itertools.product(("si", "no"), repeat=5):
        valores = dict(zip(NODOS, combinacion))
        if any(valores[n] != v for n, v in evidencia.items()):
            continue
        q = _conjunta(tablas, *combinacion)
        total += q
        for n in NODOS:
            if valores[n] == "si":
                si[n] += q
    return {n: si[n] / total for n in NODOS} if total > 0 else None


def _con_pyagrum(bn: gum.BayesNet, evidencia: dict) -> dict:
    ie = gum.LazyPropagation(bn)
    ie.setEvidence({_INTERNO[n]: v for n, v in evidencia.items()})
    ie.makeInference()
    return {n: float(ie.posterior(_INTERNO[n])[{_INTERNO[n]: "si"}]) for n in NODOS}


def _evidencia(escenario, i: int) -> dict:
    """Normaliza un escenario: acepta María o Maria, mayúsculas, «sí», True y False."""
    if not isinstance(escenario, dict):
        raise ErrorDeLaboratorio(f"El escenario {i} no es un diccionario entre llaves. Escríbelo así: "
                                 '{"Juan": "si", "María": "si"}. Para «sin evidencia», escribe {}.')
    evidencia = {}
    for clave, valor in escenario.items():
        nodo = _NOMBRES.get(_sin_tildes(clave)) if isinstance(clave, str) else None
        if nodo is None:
            raise ErrorDeLaboratorio(f"En el escenario {i} no hay un nodo llamado {clave!r}. "
                                     "Los nodos son Robo, Sismo, Alarma, Juan y María.")
        if valor is True or (isinstance(valor, str) and _sin_tildes(valor) in ("si", "s", "yes")):
            evidencia[nodo] = "si"
        elif valor is False or (isinstance(valor, str) and _sin_tildes(valor) == "no"):
            evidencia[nodo] = "no"
        else:
            raise ErrorDeLaboratorio(f"En el escenario {i}, {nodo} vale {valor!r}. Escribe \"si\" o \"no\", "
                                     "entre comillas.")
    return evidencia


def describir(evidencia: dict) -> str:
    """La evidencia en palabras: «llama Juan, no llama María»."""
    if not evidencia:
        return "sin evidencia"
    frases = {"Robo": ("hubo robo", "no hubo robo"), "Sismo": ("hubo sismo", "no hubo sismo"),
              "Alarma": ("sonó la alarma", "no sonó la alarma"), "Juan": ("llama Juan", "no llama Juan"),
              "María": ("llama María", "no llama María")}
    return ", ".join(frases[n][0 if evidencia[n] == "si" else 1] for n in NODOS if n in evidencia)


def _comprobar(bn, tablas, evidencia) -> dict:
    """Calcula con pyAgrum y compara con la cuenta a mano. Si no coinciden, avisa."""
    mano = a_mano(tablas, evidencia)
    if mano is None:
        raise ErrorDeLaboratorio(f"La evidencia «{describir(evidencia)}» es imposible con estas tablas: su probabilidad es 0. "
                                 "Revisa las tablas o cambia la evidencia.")
    calculado = _con_pyagrum(bn, evidencia)
    if any(abs(calculado[n] - mano[n]) > 1e-9 for n in NODOS):
        p.nota("pyAgrum y la cuenta a mano no coinciden en esta consulta. Avísale al docente.", "aviso")
    return calculado


def _fila(evidencia: dict, creencias: dict) -> dict:
    fila = {"Lo que sabes": describir(evidencia)}
    for n in NODOS:
        fila[f"P({n.lower()})" if n in ("Robo", "Sismo", "Alarma") else f"P(llama {n})"] = (
            ("sí" if evidencia[n] == "si" else "no") + " (evidencia)" if n in evidencia else a.pct(creencias[n]))
    return fila


@amable
def mostrar_red(tablas: dict = TABLAS) -> dict | None:
    """Dibuja la red con sus tablas y muestra la creencia en cada nodo antes de cualquier evidencia."""
    tablas = _revisar_tablas(tablas)
    bn = construir(tablas)
    g.red_de_la_alarma(tablas)
    previa = _comprobar(bn, tablas, {})
    p.mostrar_tabla([_fila({}, previa)], titulo="La creencia antes de cualquier evidencia",
                    pie="Sale de las tablas: por ejemplo, la alarma suena por un robo, por un sismo o por error.")
    numeros = 1 + 1 + 4 + 2 + 2
    p.nota(f"La red usa {numeros} números. Una tabla con todas las combinaciones de las 5 variables necesitaría "
           f"{2 ** 5 - 1}.", "info")
    return previa


@amable
def consultar(escenarios, seccion: str = "3", tablas: dict = TABLAS, titulo: str | None = None) -> list | None:
    """Calcula la creencia en cada nodo para cada escenario de evidencia, con una tabla y unas barras."""
    escenarios = a.lista("ESCENARIOS", escenarios, '[{}, {"Juan": "si"}]')
    evidencias = [_evidencia(e, i + 1) for i, e in enumerate(escenarios)]
    tablas = _revisar_tablas(tablas)
    bn = construir(tablas)
    resultados = []
    for ev in evidencias:
        creencias = _comprobar(bn, tablas, ev)
        resultados.append((ev, creencias))
        if "Robo" not in ev:
            a.anotar(seccion, "red de la alarma", describir(ev), "P(robo)", round(creencias["Robo"], 4))
    p.mostrar_tabla([_fila(ev, c) for ev, c in resultados], titulo=titulo or "La creencia en cada nodo, según lo que sabes")
    g.barras_de_creencia([(describir(ev), c["Robo"]) for ev, c in resultados if "Robo" not in ev],
                         "La creencia en el robo, según lo que sabes")
    if any("Robo" in ev for ev in evidencias):
        p.nota("Las barras no muestran los escenarios en los que el robo es evidencia: allí ya sabes si hubo robo.", "info")
    if seccion == "3" and not any(ev.get("Robo") == "si" for ev in evidencias):
        p.nota('Todavía no hay un escenario para predecir. Agrega {"Robo": "si"} a la lista para ver quién llama si hay '
               "un robo. Escríbelo en su propia línea, sin el signo #: lo que va después de un # no se ejecuta.", "info")
    return resultados


@amable
def cambiar_tablas(probs_robo, falsas_juan) -> list | None:
    """Repite el diagnóstico con otras tablas: otra probabilidad de robo y otra tasa de falsas llamadas de Juan."""
    probs_robo = a.lista_de_probabilidades("PROBS_ROBO", probs_robo, "[0.001, 0.01]", aviso_uno=True)
    falsas_juan = a.lista_de_probabilidades("FALSAS_JUAN", falsas_juan, "[0.05, 0.01]")
    filas = []
    for robo, falsa in itertools.product(probs_robo, falsas_juan):
        tablas = dict(TABLAS, Robo=robo, Juan={"si": TABLAS["Juan"]["si"], "no": falsa})
        bn = construir(tablas)
        juan = _comprobar(bn, tablas, {"Juan": "si"})["Robo"]
        dos = _comprobar(bn, tablas, {"Juan": "si", "María": "si"})["Robo"]
        filas.append({"P(robo)": a.num(robo, 4), "Juan llama sin alarma": a.num(falsa, 4),
                      "P(robo | llama Juan)": a.pct(juan), "P(robo | llaman los dos)": a.pct(dos)})
        a.anotar("7.1", "otras tablas", f"P(robo) {a.num(robo, 4)}, Juan sin alarma {a.num(falsa, 4)}",
                 "P(robo | llaman los dos)", round(dos, 4))
    original = [i for i, f in enumerate(filas) if f["P(robo)"] == "0.001" and f["Juan llama sin alarma"] == "0.05"]
    p.mostrar_tabla(filas, titulo="El diagnóstico con otras tablas", referencia=set(original),
                    pie="En gris, las tablas originales, las del libro de Russell y Norvig (AIMA), si están en tus listas.")
    return filas
