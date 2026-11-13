"""Decisiones del Laboratorio 7A (Sesión 7, Sistemas Inteligentes): la utilidad esperada y el valor de la información.

- El petrolero de Raiffa (1968), con los números que reproduce Shenoy (1995): perforar o no un pozo que puede estar
  seco, húmedo o empapado, con una prueba sísmica imperfecta que se puede comprar antes.
- La misma cuenta sirve para cualquier decisión de un solo paso. Tiene de 2 a 4 estados y 2 o 3 opciones, y una
  información que se compra antes de decidir. Así se carga una decisión propia, para el TI-1.
- Cada número sale de una cuenta a mano, como en una hoja de cálculo. Luego pyAgrum lo comprueba con un diagrama de
  influencia (ShaferShenoyLIMIDInference). pyAgrum no trae el valor de la información: sale de comparar dos utilidades
  esperadas máximas, con la prueba gratis y sin la prueba.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pyagrum as gum

import apoyo as a
import graficas as g
import presentacion as p
from apoyo import ErrorDeLaboratorio, amable

_TOLERANCIA = 1e-6


@dataclass
class Decision:
    """Una decisión de un solo paso, ya revisada."""
    estados: list
    probs: list
    opciones: dict
    resultados: dict = field(default_factory=dict)
    nombres: dict = field(default_factory=dict)    # cómo se llaman los nodos en el dibujo y en las tablas
    variables: dict = field(default_factory=dict)  # cómo se llaman las variables de la celda, para los mensajes


NOMBRES_PETROLERO = {"estado": "Pozo", "decision": "Perforar", "utilidad": "Ganancia", "informacion": "Hacer la prueba sísmica",
                     "resultado": "Resultado de la prueba", "precio": "Precio de la prueba", "la_informacion": "la prueba"}
NOMBRES_PROPIA = {"estado": "Estado", "decision": "Tu decisión", "utilidad": "Utilidad", "informacion": "Comprar la información",
                  "resultado": "Lo que dice la información", "precio": "Precio", "la_informacion": "la información"}


# ----------------------------------------------------------------------------- revisar la configuración

def _revisar(estados, probabilidades, opciones, variables: dict) -> Decision:
    ve, vp, vo = variables["estados"], variables["probs"], variables["opciones"]
    estados = a.lista(ve, estados, '["seco", "húmedo", "empapado"]')
    estados = [a.texto(f"El estado {i + 1} de {ve}", e) for i, e in enumerate(estados)]
    if not 2 <= len(estados) <= 4:
        raise ErrorDeLaboratorio(f"{ve} tiene {len(estados)} estados. Usa de 2 a 4.")
    if len(set(estados)) < len(estados):
        raise ErrorDeLaboratorio(f"{ve} repite un estado. Cada estado debe tener un nombre distinto.")
    probs = a.lista_de_probabilidades(vp, probabilidades, "[0.5, 0.3, 0.2]")
    if len(probs) != len(estados):
        raise ErrorDeLaboratorio(f"{vp} tiene {len(probs)} números y hay {len(estados)} estados. Escribe una probabilidad "
                                 "por estado, en el mismo orden. ¿Escribiste una coma decimal? Usa punto.")
    if abs(sum(probs) - 1) > _TOLERANCIA:
        raise ErrorDeLaboratorio(f"Las probabilidades de {vp} suman {a.num(sum(probs), 4)}, no 1. Revisa los números.")
    if not isinstance(opciones, dict) or not opciones:
        raise ErrorDeLaboratorio(f"{vo} debe ser un diccionario entre llaves. Escribe cada opción entre comillas, "
                                 'dos puntos y la lista de sus pagos. Por ejemplo: {"perforar": [-70, 50, 200], '
                                 '"no perforar": [0, 0, 0]}.')
    if not 2 <= len(opciones) <= 3:
        cuantas = "una sola opción" if len(opciones) == 1 else f"{len(opciones)} opciones"
        raise ErrorDeLaboratorio(f"{vo} tiene {cuantas}. Usa 2 o 3.")
    revisadas = {}
    for nombre, pagos in opciones.items():
        nombre = a.texto(f"El nombre de una opción de {vo}", nombre)
        pagos = a.lista(f'{vo}["{nombre}"]', pagos, "[-70, 50, 200]")
        if len(pagos) != len(estados):
            raise ErrorDeLaboratorio(f'{vo}["{nombre}"] tiene {len(pagos)} pagos y hay {len(estados)} estados. Escribe un '
                                     "pago por estado, en el orden de los estados. ¿Escribiste una coma decimal? Usa punto.")
        revisadas[nombre] = [a.numero(f'El pago {j + 1} de {vo}["{nombre}"]', v) for j, v in enumerate(pagos)]
    return Decision(estados, probs, revisadas, variables=variables)


def _revisar_resultados(dec: Decision, resultados, variable: str) -> dict:
    if not isinstance(resultados, dict) or len(resultados) < 2:
        raise ErrorDeLaboratorio(f"{variable} debe ser un diccionario con al menos 2 resultados. Escribe cada resultado "
                                 "entre comillas, dos puntos y la lista de su probabilidad en cada estado.")
    if len(resultados) > 4:
        raise ErrorDeLaboratorio(f"{variable} tiene {len(resultados)} resultados. Usa de 2 a 4.")
    revisados = {}
    for nombre, probs in resultados.items():
        nombre = a.texto(f"El nombre de un resultado de {variable}", nombre)
        if nombre == "ninguno":
            raise ErrorDeLaboratorio(f"{variable} no puede tener un resultado llamado «ninguno»: el notebook usa ese nombre "
                                     "cuando no se compra la información. Cámbialo.")
        probs = a.lista_de_probabilidades(f'{variable}["{nombre}"]', probs, "[0.6, 0.3, 0.1]")
        if len(probs) != len(dec.estados):
            raise ErrorDeLaboratorio(f'{variable}["{nombre}"] tiene {len(probs)} números y hay {len(dec.estados)} estados. '
                                     "Escribe una probabilidad por estado, en el orden de los estados.")
        revisados[nombre] = probs
    for j, estado in enumerate(dec.estados):
        columna = [v[j] for v in revisados.values()]
        if abs(sum(columna) - 1) > _TOLERANCIA:
            cuenta = " + ".join(a.num(x, 4) for x in columna)
            raise ErrorDeLaboratorio(f"La columna {j + 1} de {variable}, la del estado «{estado}», suma {cuenta} = "
                                     f"{a.num(sum(columna), 4)}, no 1. Cada columna es un estado y debe sumar 1. "
                                     "Las filas, los resultados, no tienen que sumar 1.")
    return revisados


def _precios(precios, variable: str) -> list:
    return a.lista_de_numeros(variable, precios, "[5, 10, 15]", minimo=0)


# ----------------------------------------------------------------------------- las cuentas a mano

def utilidades(dec: Decision, probs: list) -> dict:
    """La utilidad esperada de cada opción: la suma de probabilidad por pago."""
    return {o: sum(q * u for q, u in zip(probs, pagos)) for o, pagos in dec.opciones.items()}


def mejor(ue: dict) -> tuple:
    """La opción de mayor utilidad esperada. Si dos empatan, lo dice."""
    tope = max(ue.values())
    ganadoras = [o for o, v in ue.items() if abs(v - tope) < 1e-9]
    return (ganadoras[0] if len(ganadoras) == 1 else "empate: " + " o ".join(ganadoras)), tope


def analizar(dec: Decision, resultados: dict | None = None) -> dict:
    """Todas las cuentas: sin información, con la información gratis y con la información perfecta."""
    resultados = dec.resultados if resultados is None else resultados
    ue_sin = utilidades(dec, dec.probs)
    decision_sin, valor_sin = mejor(ue_sin)
    por_resultado, valor_gratis = {}, 0.0
    for r, verosimilitud in (resultados or {}).items():
        p_r = sum(q * v for q, v in zip(dec.probs, verosimilitud))
        if p_r <= 0:
            por_resultado[r] = {"p": 0.0, "posterior": None, "ue": None, "decision": "nunca ocurre"}
            continue
        posterior = [q * v / p_r for q, v in zip(dec.probs, verosimilitud)]
        ue = utilidades(dec, posterior)
        decision, valor = mejor(ue)
        valor_gratis += p_r * valor
        por_resultado[r] = {"p": p_r, "posterior": posterior, "ue": ue, "decision": decision}
    valor_perfecta = sum(q * max(pagos[j] for pagos in dec.opciones.values()) for j, q in enumerate(dec.probs))
    return {"ue_sin": ue_sin, "decision_sin": decision_sin, "valor_sin": valor_sin, "por_resultado": por_resultado,
            "valor_gratis": valor_gratis, "vi": valor_gratis - valor_sin, "valor_perfecta": valor_perfecta,
            "vip": valor_perfecta - valor_sin}


def _mezclar(dec: Decision, confiabilidad: float) -> dict:
    """Una prueba menos informativa. Con 0 da cada resultado con la misma frecuencia en todos los estados. Con 1 es la original."""
    resultados = {}
    for r, verosimilitud in dec.resultados.items():
        marginal = sum(q * v for q, v in zip(dec.probs, verosimilitud))
        resultados[r] = [confiabilidad * v + (1 - confiabilidad) * marginal for v in verosimilitud]
    return resultados


# ----------------------------------------------------------------------------- la comprobación con pyAgrum

def diagrama(dec: Decision, precio: float = 0.0) -> gum.InfluenceDiagram:
    """El diagrama de influencia: dos decisiones (comprar la información y decidir), dos azares y dos utilidades."""
    d = gum.InfluenceDiagram()

    def variable(nombre, etiquetas):
        v = gum.LabelizedVariable(nombre, nombre, 0)
        for e in etiquetas:
            v.addLabel(e)
        return v
    nodos = {"Estado": d.addChanceNode(variable("Estado", dec.estados)),
             "Informacion": d.addDecisionNode(variable("Informacion", ["no comprar", "comprar"])),
             "Resultado": d.addChanceNode(variable("Resultado", list(dec.resultados) + ["ninguno"])),
             "Decision": d.addDecisionNode(variable("Decision", list(dec.opciones))),
             "Utilidad": d.addUtilityNode(gum.LabelizedVariable("Utilidad", "Utilidad", 1)),
             "Precio": d.addUtilityNode(gum.LabelizedVariable("Precio", "Precio", 1))}
    for de, a_ in (("Estado", "Resultado"), ("Informacion", "Resultado"), ("Informacion", "Decision"),
                   ("Resultado", "Decision"), ("Decision", "Utilidad"), ("Estado", "Utilidad"), ("Informacion", "Precio")):
        d.addArc(nodos[de], nodos[a_])
    d.cpt("Estado").fillWith(dec.probs)
    n = len(dec.resultados)
    for j, e in enumerate(dec.estados):
        # Sin comprar la información, el resultado siempre es «ninguno»
        d.cpt("Resultado")[{"Estado": e, "Informacion": "no comprar"}] = [0] * n + [1]
        d.cpt("Resultado")[{"Estado": e, "Informacion": "comprar"}] = [v[j] for v in dec.resultados.values()] + [0]
        for o, pagos in dec.opciones.items():
            d.utility("Utilidad")[{"Estado": e, "Decision": o}] = pagos[j]
    d.utility("Precio")[{"Informacion": "comprar"}] = -precio
    d.utility("Precio")[{"Informacion": "no comprar"}] = 0
    return d


def con_pyagrum(dec: Decision) -> dict:
    """La utilidad esperada máxima con la información gratis y sin ella, y su diferencia: el valor de la información."""
    salida = {}
    for clave, forzar in (("gratis", None), ("sin", "no comprar")):
        ie = gum.ShaferShenoyLIMIDInference(diagrama(dec))
        if forzar:
            ie.setEvidence({"Informacion": forzar})   # se fuerza la decisión «no comprar»
        ie.makeInference()
        salida[clave] = float(ie.MEU()["mean"])
    salida["vi"] = salida["gratis"] - salida["sin"]
    return salida


def _comprobar(dec: Decision, cuentas: dict) -> None:
    pg = con_pyagrum(dec)
    if abs(pg["gratis"] - cuentas["valor_gratis"]) > 1e-6 or abs(pg["sin"] - cuentas["valor_sin"]) > 1e-6:
        p.nota("pyAgrum y la cuenta a mano no coinciden. Avísale al docente.", "aviso")
    else:
        p.nota(f"pyAgrum resolvió el diagrama de influencia y da lo mismo que la cuenta a mano: "
               f"{a.num(pg['gratis'])} con {dec.nombres['la_informacion']} gratis, {a.num(pg['sin'])} sin ella "
               f"y {a.num(pg['vi'])} de valor de la información.", "exito", "Comprobación con pyAgrum")


# ----------------------------------------------------------------------------- tablas

def _tabla_sin_informacion(dec: Decision, cuentas: dict, titulo: str) -> None:
    filas = []
    for o, pagos in dec.opciones.items():
        fila = {"Opción": o}
        for e, q, u in zip(dec.estados, dec.probs, pagos):
            fila[f"{e} (P = {a.num(q, 4)})"] = f"{a.num(u)} × {a.num(q, 4)} = {a.num(q * u)}"
        fila["Utilidad esperada"] = a.num(cuentas["ue_sin"][o])
        filas.append(fila)
    ganadoras = {i for i, o in enumerate(dec.opciones) if abs(cuentas["ue_sin"][o] - cuentas["valor_sin"]) < 1e-9}
    p.mostrar_tabla(filas, titulo=titulo, resaltar=ganadoras,
                    pie=f"Cada casilla es pago × probabilidad. Mejor decisión: {cuentas['decision_sin']}, "
                        f"con {a.num(cuentas['valor_sin'])}.")


def _tabla_por_resultado(dec: Decision, cuentas: dict) -> None:
    filas, creencias = [], []
    for r, c in cuentas["por_resultado"].items():
        fila = {f"{dec.nombres['resultado']}": r, "P(resultado)": a.prob(c["p"])}
        for o in dec.opciones:
            fila[f"UE de {o}"] = a.num(c["ue"][o]) if c["ue"] else "-"
        fila["Mejor decisión"] = c["decision"]
        filas.append(fila)
        verosimilitud = dec.resultados[r]
        creencia = {f"{dec.nombres['resultado']}": r,
                    "P(resultado), sumando los estados": " + ".join(f"{a.num(q, 4)} × {a.num(v, 4)}" for q, v in
                                                                    zip(dec.probs, verosimilitud)) + f" = {a.prob(c['p'])}"}
        for j, e in enumerate(dec.estados):
            creencia[f"P({e} | resultado)"] = (f"{c['posterior'][j]:.3f}" if c["posterior"] else "-")
        creencias.append(creencia)
    p.mostrar_tabla(filas, titulo=f"Lo que conviene decidir según lo que diga {dec.nombres['la_informacion']}",
                    pie="UE es la utilidad esperada. Cada resultado cambia la creencia en cada estado, y con ella la decisión.")
    p.desplegable("Ver de dónde sale P(resultado) y cómo cambia la creencia en cada estado (la regla de Bayes)",
                  p.tabla_html(creencias, pie="Cada creencia es la probabilidad del estado por la del resultado en ese "
                                              "estado, dividida por P(resultado). Las cifras van redondeadas."))


def _tabla_valor(dec: Decision, cuentas: dict) -> None:
    info = dec.nombres["la_informacion"]
    mejores = [max(pagos[j] for pagos in dec.opciones.values()) for j in range(len(dec.estados))]
    perfecta = " + ".join(f"{a.num(q, 4)} × {a.num(m)}" for q, m in zip(dec.probs, mejores))
    filas = [{"Cómo decides": f"sin {info}: {cuentas['decision_sin']}", "Utilidad esperada": a.num(cuentas["valor_sin"]),
              "Diferencia con decidir sin información": "0"},
             {"Cómo decides": f"con {info} gratis: según su resultado", "Utilidad esperada": a.num(cuentas["valor_gratis"]),
              "Diferencia con decidir sin información": f"{a.num(cuentas['vi'])}: el valor de la información"},
             {"Cómo decides": "con información perfecta: sabes el estado antes de decidir",
              "Utilidad esperada": a.num(cuentas["valor_perfecta"]),
              "Diferencia con decidir sin información": f"{a.num(cuentas['vip'])}: el tope de cualquier información"}]
    p.mostrar_tabla(filas, titulo="¿Cuánto vale saber antes de decidir?", referencia={0, 2}, resaltar={1},
                    pie=f"Con información perfecta eliges lo mejor en cada estado: {perfecta} = "
                        f"{a.num(cuentas['valor_perfecta'])}. Ninguna información real vale más.")


def _tabla_precios(dec: Decision, cuentas: dict, precios: list, seccion: str | None) -> None:
    filas = []
    for precio in precios:
        neto = cuentas["valor_gratis"] - precio
        margen = cuentas["vi"] - precio
        conviene = ("sí: ganas " + a.num(margen) if margen > 1e-9 else
                    "no: pierdes " + a.num(-margen) if margen < -1e-9 else "da lo mismo")
        filas.append({"Precio": a.num(precio), "Valor de la información": a.num(cuentas["vi"]),
                      "Utilidad esperada si la compras": a.num(neto), "¿Conviene comprarla?": conviene})
        if seccion:
            a.anotar(seccion, "valor de la información", f"precio {a.num(precio)}",
                     "comprar" if margen > 1e-9 else "no comprar", round(cuentas["vi"], 4))
    p.mostrar_tabla(filas, titulo=f"¿Conviene pagar {dec.nombres['la_informacion']}?",
                    pie=f"Conviene si su valor supera su precio. Sin ella, la decisión vale {a.num(cuentas['valor_sin'])}.")


# ----------------------------------------------------------------------------- 5. el petrolero, sin la prueba

@amable
def decidir(estados, probabilidades, opciones, nombres: dict | None = None, variables: dict | None = None,
            seccion: str | None = "5") -> Decision | None:
    """La utilidad esperada de cada opción, sin más información, con el diagrama de influencia más simple."""
    variables = variables or {"estados": "ESTADOS", "probs": "PROBABILIDADES", "opciones": "OPCIONES"}
    dec = _revisar(estados, probabilidades, opciones, variables)
    dec.nombres = nombres or NOMBRES_PETROLERO
    cuentas = analizar(dec, {})
    g.diagrama_de_influencia(dec.nombres, con_informacion=False)
    _tabla_sin_informacion(dec, cuentas, "La utilidad esperada de cada opción, sin más información")
    if seccion:
        config = "; ".join(f"{e} {a.num(q, 4)}" for e, q in zip(dec.estados, dec.probs))
        a.anotar(seccion, "decidir sin información", config, f"mejor: {cuentas['decision_sin']}",
                 round(cuentas["valor_sin"], 4))
    return dec


@amable
def otros_pagos(dec: Decision, opcion: str, estado: str, pagos) -> list | None:
    """Cambia un pago y muestra desde dónde cambia la decisión, sin tocar la configuración del petrolero."""
    if dec is None:
        raise ErrorDeLaboratorio("Primero ejecuta sin errores la celda anterior, la de la decisión.")
    if opcion not in dec.opciones:
        raise ErrorDeLaboratorio(f"No encuentro la opción «{opcion}» en la celda anterior. Sus opciones son: "
                                 + ", ".join(dec.opciones) + ".")
    if estado not in dec.estados:
        raise ErrorDeLaboratorio(f"No encuentro el estado «{estado}» en la celda anterior. Sus estados son: "
                                 + ", ".join(dec.estados) + ".")
    pagos = a.lista_de_numeros("PAGOS_EMPAPADO", pagos, "[200, 150, 100, 50]")
    j = dec.estados.index(estado)
    filas = []
    for pago in pagos:
        opciones = {o: list(v) for o, v in dec.opciones.items()}
        opciones[opcion][j] = pago
        ue = utilidades(Decision(dec.estados, dec.probs, opciones), dec.probs)
        decision, _ = mejor(ue)
        fila = {f"Pago de {opcion} si está {estado}": a.num(pago)}
        fila.update({f"UE de {o}": a.num(v) for o, v in ue.items()})
        fila["Mejor decisión"] = decision
        filas.append(fila)
        a.anotar("7.2", "otro pago", f"pago de {opcion} si {estado}: {a.num(pago)}", f"mejor: {decision}",
                 round(ue[opcion], 4))
    original = {i for i, v in enumerate(pagos) if abs(v - dec.opciones[opcion][j]) < 1e-9}
    p.mostrar_tabla(filas, titulo="¿Desde qué pago cambia la decisión?", referencia=original,
                    pie="En gris, el pago original, si está en tu lista.")
    if len(pagos) == 1:
        p.nota("Agrega otros pagos a la lista, como 100 y 50, para ver dónde cambia la decisión.", "info")
    return filas


# ----------------------------------------------------------------------------- 6. el valor de la información

@amable
def valor_de_la_informacion(dec: Decision, resultados, precios, variable: str = "RESULTADOS",
                            variable_precios: str = "PRECIOS", seccion: str | None = "6") -> Decision | None:
    """La decisión según cada resultado, el valor de la información y la comparación con su precio."""
    if dec is None:
        raise ErrorDeLaboratorio("Primero ejecuta sin errores la celda de la decisión, en la sección anterior.")
    dec = Decision(dec.estados, dec.probs, dec.opciones, _revisar_resultados(dec, resultados, variable), dec.nombres,
                   dec.variables)
    precios = _precios(precios, variable_precios)
    cuentas = analizar(dec)
    g.diagrama_de_influencia(dec.nombres, con_informacion=True)
    _tabla_por_resultado(dec, cuentas)
    _tabla_valor(dec, cuentas)
    _tabla_precios(dec, cuentas, precios, seccion)
    _comprobar(dec, cuentas)
    if seccion:
        a.anotar(seccion, "información perfecta", "saber el estado antes de decidir", "tope del valor de la información",
                 round(cuentas["vip"], 4))
        if len(precios) == 1:
            p.nota("Agrega otros precios a la lista, como 5 y 15, para ver desde dónde ya no conviene probar.", "info")
    return dec


@amable
def curva_de_confiabilidad(dec: Decision, confiabilidades, precio) -> list | None:
    """El valor de la información según qué tanto informa la prueba, comparado con su precio y con la información perfecta."""
    if dec is None or not dec.resultados:
        raise ErrorDeLaboratorio("Primero ejecuta sin errores la celda de la sección 6, la de la prueba.")
    niveles = a.lista_de_probabilidades("CONFIABILIDADES", confiabilidades, "[0, 0.5, 1]")
    precio = a.numero("PRECIO", precio, 0)
    vip = analizar(dec)["vip"]
    malla = [i / 100 for i in range(101)]
    curva = [analizar(dec, _mezclar(dec, c))["vi"] for c in malla]
    desde = next((c for c, v in zip(malla, curva) if v > precio + 1e-9), None)
    filas = []
    for c in niveles:
        vi = analizar(dec, _mezclar(dec, c))["vi"]
        filas.append({"Confiabilidad": a.num(c, 2), "Valor de la información": f"{vi:.2f}",
                      f"¿Conviene con precio {a.num(precio)}?": "sí" if vi > precio + 1e-9 else "no"})
        a.anotar("7.3", "confiabilidad de la prueba", f"confiabilidad {a.num(c, 2)}, precio {a.num(precio)}",
                 "comprar" if vi > precio + 1e-9 else "no comprar", round(vi, 4))
    g.curva_de_confiabilidad(malla, curva, niveles, [analizar(dec, _mezclar(dec, c))["vi"] for c in niveles], precio, vip)
    p.mostrar_tabla(filas, titulo="El valor de la prueba según qué tanto informa",
                    pie=("Desde una confiabilidad de " + a.num(desde, 2) + ", la prueba vale más que su precio." if desde
                         is not None else "Con ninguna confiabilidad, la prueba vale más que su precio."))
    return filas


# ----------------------------------------------------------------------------- 7.3. tu propia decisión

@amable
def mi_decision(estados, probabilidades, opciones, resultados, precios) -> Decision | None:
    """Tu decisión, en el formato del petrolero: la utilidad esperada, el valor de la información y el de la perfecta."""
    variables = {"estados": "ESTADOS_TI", "probs": "PROBABILIDADES_TI", "opciones": "OPCIONES_TI"}
    dec = _revisar(estados, probabilidades, opciones, variables)
    dec.nombres = NOMBRES_PROPIA
    dec.resultados = _revisar_resultados(dec, resultados, "RESULTADOS_TI")
    precios = _precios(precios, "PRECIOS_TI")
    cuentas = analizar(dec)
    g.diagrama_de_influencia(dec.nombres, con_informacion=True)
    _tabla_sin_informacion(dec, cuentas, "Tu decisión: la utilidad esperada de cada opción, sin más información")
    _tabla_por_resultado(dec, cuentas)
    _tabla_valor(dec, cuentas)
    _tabla_precios(dec, cuentas, precios, None)
    _comprobar(dec, cuentas)
    return dec
