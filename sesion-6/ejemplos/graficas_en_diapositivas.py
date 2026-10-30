"""Pone en las diapositivas las gráficas hechas con los números de salidas/ (correr después de los ejemplos).

Cada gráfica va en el HTML entre dos comentarios, <!--DATOS:nombre--> y <!--/DATOS:nombre-->.
Este script reemplaza lo que haya entre ellos, así que se puede correr cuantas veces se quiera.

Uso, desde esta carpeta:  python graficas_en_diapositivas.py
Solo usa la biblioteca estándar de Python.
"""
import json
import re
from html import escape
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SALIDAS = AQUI / "salidas"
SESION = AQUI.parent
CIAN, AMBAR, VIOLETA, VERDE, ROJO = "#38bdf8", "#f5b942", "#a78bfa", "#4ade80", "#f87171"
LINEA, TENUE, TEXTO, PANEL = "#2a3550", "#a3adc2", "#e8ecf4", "#111827"
ESTILO = "<style>.cs{font-size:15px;fill:#a3adc2}.cl{font-size:17px;font-weight:700}.ct{font-size:16px;fill:#e8ecf4}</style>"


def leer(nombre: str) -> dict:
    return json.loads((SALIDAS / nombre).read_text(encoding="utf-8"))


def num(x: float, dec: int = 2) -> str:
    return f"{x:.{dec}f}".replace(".", ",")


def pct(x: float, dec: int = 1) -> str:
    return num(100 * x, dec) + " %"


# ---------------------------------------------------------------- charla inicial: árboles

def clima_tabla(d: dict) -> str:
    filas = ["<tr><th>#</th><th>pronóstico</th><th>temperatura</th><th>humedad</th><th>viento</th><th>¿juega?</th></tr>"]
    for i, f in enumerate(d["quinlan"]["tabla"], 1):
        clase = '<td class="hi">sí</td>' if f[4] == "P" else "<td>no</td>"
        filas.append(f"<tr><td>{i}</td><td>{f[0]}</td><td>{f[1]}</td><td>{f[2]}</td><td>{f[3]}</td>{clase}</tr>")
    return f'<table class="tbl xs num">{"".join(filas)}</table>'


def clima_ganancias(d: dict) -> str:
    g = d["quinlan"]["ganancias_raiz"]
    orden = sorted(g, key=g.get, reverse=True)
    maximo = max(g.values())
    filas = []
    for i, k in enumerate(orden):
        cls = "bar" if i == 0 else "bar v"
        filas.append(f'<span class="lb">{k}</span><span class="{cls}" style="width:{100 * g[k] / maximo:.0f}%"></span>'
                     f'<span class="val">{num(g[k], 3)}</span>')
    return f'<div class="bars">{"".join(filas)}</div>'


def _condicion(atributo: str, umbral: float):
    """La pregunta de un nodo y los rótulos de sus dos ramas (izquierda: se cumple «atributo ≤ umbral»)."""
    if atributo == "mujer":
        return "¿mujer?", "no", "sí"
    if atributo == "clase":
        return ("¿1.ª clase?", "sí", "no") if umbral < 2 else ("¿1.ª o 2.ª clase?", "sí", "no")
    if atributo == "edad":
        return f"¿edad ≤ {num(umbral, 1)}?", "sí", "no"
    if atributo == "tarifa":
        return f"¿tarifa ≤ {num(umbral, 1)} £?", "sí", "no"
    if atributo == "hermanos_o_conyuge":
        return f"¿≤ {int(umbral)} hermanos o cónyuge?", "sí", "no"
    if atributo == "padres_o_hijos":
        return f"¿≤ {int(umbral)} padres o hijos?", "sí", "no"
    return f"¿{atributo} ≤ {num(umbral, 1)}?", "sí", "no"


def titanic_arbol(d: dict) -> str:
    nodos = {n["id"]: n for n in d["titanic"]["arbol3"]}
    ancho, alto = 1180, 430
    pos, partes = {}, []

    def ubicar(i, nivel, x0, x1):
        n = nodos[i]
        pos[i] = ((x0 + x1) / 2, 30 + nivel * 118)
        if n["atributo"]:
            ubicar(n["si"], nivel + 1, x0, (x0 + x1) / 2)
            ubicar(n["no"], nivel + 1, (x0 + x1) / 2, x1)
    ubicar(0, 0, 0, ancho)
    for i, n in nodos.items():
        if n["atributo"]:
            pregunta, si, no = _condicion(n["atributo"], n["umbral"])
            for hijo, rot in ((n["si"], si), (n["no"], no)):
                (x0, y0), (x1, y1) = pos[i], pos[hijo]
                partes.append(f'<line x1="{x0:.0f}" y1="{y0 + 18:.0f}" x2="{x1:.0f}" y2="{y1 - 22:.0f}" stroke="{LINEA}" stroke-width="2"/>'
                              f'<text x="{(x0 + x1) / 2:.0f}" y="{(y0 + y1) / 2 + 2:.0f}" text-anchor="middle" class="cs">{rot}</text>')
    for i, n in nodos.items():
        x, y = pos[i]
        if n["atributo"]:
            pregunta = _condicion(n["atributo"], n["umbral"])[0]
            w = 14 + 9.4 * len(pregunta)
            partes.append(f'<rect x="{x - w / 2:.0f}" y="{y - 18:.0f}" width="{w:.0f}" height="36" rx="8" fill="{PANEL}" stroke="{CIAN}"/>'
                          f'<text x="{x:.0f}" y="{y + 6:.0f}" text-anchor="middle" class="ct">{escape(pregunta)}</text>')
        else:
            vive, muere = n["sobreviven"], n["no_sobreviven"]
            color = VERDE if vive > muere else ROJO
            texto = "sobrevive" if vive > muere else "no sobrevive"
            partes.append(f'<rect x="{x - 66:.0f}" y="{y - 22:.0f}" width="132" height="48" rx="8" fill="{PANEL}" stroke="{color}" stroke-width="2"/>'
                          f'<text x="{x:.0f}" y="{y - 2:.0f}" text-anchor="middle" class="ct" style="fill:{color};font-weight:700">{texto}</text>'
                          f'<text x="{x:.0f}" y="{y + 18:.0f}" text-anchor="middle" class="cs">{max(vive, muere)} de {vive + muere}</text>')
    return (f'<svg class="diagram" viewBox="0 0 {ancho} {alto}" role="img" aria-label="Árbol de decisión de profundidad 3 '
            f'aprendido con los {d["titanic"]["pasajeros"]} pasajeros del Titanic: la primera pregunta es si la persona es mujer">'
            + ESTILO + "".join(partes) + "</svg>")


def _linea(puntos, x0, y0, ancho, alto, ymin, ymax, n):
    return " ".join(f"{x0 + ancho * i / (n - 1):.1f},{y0 + alto * (1 - (v - ymin) / (ymax - ymin)):.1f}" for i, v in enumerate(puntos))


def titanic_profundidad(d: dict) -> str:
    p = d["titanic"]["profundidades"]
    n = len(p)
    x0, y0, ancho, alto, ymin, ymax = 90, 20, 760, 280, 0.70, 1.00
    s = [f'<line x1="{x0}" y1="{y0 + alto}" x2="{x0 + ancho}" y2="{y0 + alto}" stroke="{LINEA}"/>']
    for k in range(0, 4):
        v = ymin + (ymax - ymin) * k / 3
        y = y0 + alto * (1 - k / 3)
        s.append(f'<text x="{x0 - 8}" y="{y + 5:.0f}" text-anchor="end" class="cs">{pct(v, 0)}</text>'
                 f'<line x1="{x0}" y1="{y:.0f}" x2="{x0 + ancho}" y2="{y:.0f}" stroke="#1c2538"/>')
    for i, q in enumerate(p):
        x = x0 + ancho * i / (n - 1)
        s.append(f'<text x="{x:.0f}" y="{y0 + alto + 22}" text-anchor="middle" class="cs">{q["profundidad"] if q["profundidad"] != "sin límite" else "∞"}</text>')
    s.append(f'<text x="{x0 + ancho / 2}" y="{y0 + alto + 46}" text-anchor="middle" class="cs">profundidad máxima del árbol</text>')
    base = d["titanic"]["linea_base"]
    entrena = [q["entrenamiento"] for q in p]
    valida = [q["validacion_cruzada"] for q in p]
    mejor = max(range(n), key=lambda i: valida[i])
    xm = x0 + ancho * mejor / (n - 1)
    s.append(f'<polyline points="{_linea(entrena, x0, y0, ancho, alto, ymin, ymax, n)}" fill="none" stroke="{CIAN}" stroke-width="3"/>'
             f'<text x="{x0 + ancho - 4}" y="{y0 + alto * (1 - (entrena[-1] - ymin) / (ymax - ymin)) - 10:.0f}" text-anchor="end" class="cl" fill="{CIAN}">entrenamiento · {pct(entrena[-1], 0)}</text>'
             f'<g class="fragment"><polyline points="{_linea(valida, x0, y0, ancho, alto, ymin, ymax, n)}" fill="none" stroke="{AMBAR}" stroke-width="3"/>'
             f'<text x="{x0 + ancho - 4}" y="{y0 + alto * (1 - (valida[-1] - ymin) / (ymax - ymin)) + 24:.0f}" text-anchor="end" class="cl" fill="{AMBAR}">validación cruzada · {pct(valida[-1], 0)}</text></g>'
             f'<g class="fragment"><line x1="{xm:.0f}" y1="{y0}" x2="{xm:.0f}" y2="{y0 + alto}" stroke="{VERDE}" stroke-dasharray="6 5" stroke-width="2"/>'
             f'<text x="{xm + 8:.0f}" y="{y0 + 18}" class="cl" fill="{VERDE}">la mejor: profundidad {p[mejor]["profundidad"]} · {pct(valida[mejor], 0)}</text></g>')
    return (f'<svg class="diagram" viewBox="0 0 900 360" role="img" aria-label="Aciertos del árbol del Titanic según su profundidad: '
            f'en entrenamiento suben hasta {pct(entrena[-1], 0)}; en validación cruzada el mejor es {pct(valida[mejor], 0)} con profundidad '
            f'{p[mejor]["profundidad"]} y bajan a {pct(valida[-1], 0)} sin límite">' + ESTILO + "".join(s) + "</svg>")


def regla_experto(d: dict) -> str:
    return pct(d["titanic"]["regla_experto"])


def arbol3_cv(d: dict) -> str:
    return pct({q["profundidad"]: q for q in d["titanic"]["profundidades"]}[3]["validacion_cruzada"])


def titanic_ensambles(d: dict) -> str:
    t = d["titanic"]
    p = {q["profundidad"]: q for q in t["profundidades"]}
    e = t["ensambles"]
    filas = [("Un árbol de profundidad 3", p[3]["validacion_cruzada"], p[3]["desviacion"]),
             ("Bosque aleatorio, 300 árboles", e["bosque aleatorio"]["validacion_cruzada"], e["bosque aleatorio"]["desviacion"]),
             ("Boosting por gradiente", e["boosting por gradiente"]["validacion_cruzada"], e["boosting por gradiente"]["desviacion"])]
    cuerpo = "".join(f"<tr><td>{a}</td><td>{pct(b)}</td><td>± {num(100 * c, 1)}</td></tr>" for a, b, c in filas)
    return f'<table class="tbl num"><tr><th>Titanic</th><th>Aciertos</th><th>Variación entre partes</th></tr>{cuerpo}</table>'


def titanic_pliegues(d: dict) -> str:
    t = d["titanic"]
    celdas = "".join(f'<span class="fold fragment"><b>Parte {i}</b>{pct(v)}</span>' for i, v in enumerate(t["pliegues_arbol3"], 1))
    media = sum(t["pliegues_arbol3"]) / len(t["pliegues_arbol3"])
    return f'<div class="folds">{celdas}<span class="fold avg fragment"><b>Promedio</b>{pct(media)}</span></div>'


def credito_curva(d: dict) -> str:
    c = d["credito"]
    curva = c["curva"]
    x0, y0, ancho, alto, ymax = 90, 20, 760, 270, 1600
    xs = lambda u: x0 + ancho * (u - 0.05) / 0.90
    ys = lambda v: y0 + alto * (1 - v / ymax)
    s = [f'<line x1="{x0}" y1="{y0 + alto}" x2="{x0 + ancho}" y2="{y0 + alto}" stroke="{LINEA}"/>']
    for v in (0, 400, 800, 1200, 1600):
        s.append(f'<text x="{x0 - 8}" y="{ys(v) + 5:.0f}" text-anchor="end" class="cs">{v}</text>'
                 f'<line x1="{x0}" y1="{ys(v):.0f}" x2="{x0 + ancho}" y2="{ys(v):.0f}" stroke="#1c2538"/>')
    for u in (0.1, 0.3, 0.5, 0.7, 0.9):
        s.append(f'<text x="{xs(u):.0f}" y="{y0 + alto + 22}" text-anchor="middle" class="cs">{num(u, 1)}</text>')
    s.append(f'<text x="{x0 + ancho / 2}" y="{y0 + alto + 46}" text-anchor="middle" class="cs">umbral: probabilidad de ser mal pagador desde la cual se rechaza</text>'
             f'<text x="{x0 - 58}" y="{y0 + alto / 2}" text-anchor="middle" class="cs" transform="rotate(-90 {x0 - 58} {y0 + alto / 2})">costo total</text>')
    puntos = " ".join(f"{xs(p['umbral']):.1f},{ys(p['costo']):.1f}" for p in curva)
    s.append(f'<line x1="{x0}" y1="{ys(c["rechazar_a_todos"]):.0f}" x2="{x0 + ancho}" y2="{ys(c["rechazar_a_todos"]):.0f}" stroke="{TENUE}" stroke-dasharray="5 5"/>'
             f'<text x="{x0 + ancho - 4}" y="{ys(c["rechazar_a_todos"]) - 8:.0f}" text-anchor="end" class="cs">rechazar a todos: {c["rechazar_a_todos"]}</text>'
             f'<polyline points="{puntos}" fill="none" stroke="{AMBAR}" stroke-width="3"/>')
    for clave, color, texto, dy in (("umbral_0_5", ROJO, "umbral 0,5", -14), ("umbral_costo", VERDE, "umbral 1/6", 28)):
        p = c[clave]
        s.append(f'<g class="fragment"><circle cx="{xs(p["umbral"]):.0f}" cy="{ys(p["costo"]):.0f}" r="8" fill="{color}"/>'
                 f'<text x="{xs(p["umbral"]) + 12:.0f}" y="{ys(p["costo"]) + dy:.0f}" class="cl" fill="{color}">{texto}: costo {p["costo"]}, '
                 f'aciertos {pct(p["exactitud"], 0)}</text></g>')
    return (f'<svg class="diagram" viewBox="0 0 900 350" role="img" aria-label="Costo total del bosque aleatorio en el German Credit '
            f'según el umbral: con 0,5 cuesta {c["umbral_0_5"]["costo"]} y acierta {pct(c["umbral_0_5"]["exactitud"], 0)}; con 1/6 cuesta '
            f'{c["umbral_costo"]["costo"]} y acierta {pct(c["umbral_costo"]["exactitud"], 0)}">' + ESTILO + "".join(s) + "</svg>")


def hongos(d: dict) -> str:
    h = d["hongos"]
    miles = f"{h['hongos']:,}".replace(",", " ")
    return (f"Mushroom (UCI): con una sola pregunta, el olor, una regla clasifica bien el {pct(h['acierto_regla_olor'], 2)} "
            f"de los {miles} hongos.")


# ---------------------------------------------------------------- charla intermedia: refuerzo

def _cuadricula(valores: dict, politica: dict, celda=120, x0=10, y0=10, flechas=True, tam_valor=20) -> str:
    s = []
    for f in (3, 2, 1):
        for c in (1, 2, 3, 4):
            x, y = x0 + (c - 1) * celda, y0 + (3 - f) * celda
            clave = f"{c},{f}"
            if (c, f) == (2, 2):
                s.append(f'<rect x="{x}" y="{y}" width="{celda}" height="{celda}" fill="#2a3550"/>')
                continue
            fondo = {"4,3": "rgba(74,222,128,.25)", "4,2": "rgba(248,113,113,.25)"}.get(clave, PANEL)
            s.append(f'<rect x="{x}" y="{y}" width="{celda}" height="{celda}" fill="{fondo}" stroke="{LINEA}" stroke-width="2"/>')
            if clave in ("4,3", "4,2"):
                s.append(f'<text x="{x + celda / 2}" y="{y + celda / 2 + 10}" text-anchor="middle" style="font-size:{tam_valor + 10}px;font-weight:800;fill:{VERDE if clave == "4,3" else ROJO}">{"+1" if clave == "4,3" else "−1"}</text>')
                continue
            if valores is not None:
                s.append(f'<text x="{x + celda / 2}" y="{y + celda - 14}" text-anchor="middle" style="font-size:{tam_valor}px;fill:{TEXTO}">{num(valores[clave], 3)}</text>')
            if flechas and clave in politica:
                s.append(f'<text x="{x + celda / 2}" y="{y + celda / 2 + (2 if valores is not None else 14)}" text-anchor="middle" style="font-size:{int(celda * 0.36)}px;fill:{CIAN}">{politica[clave]}</text>')
    return "".join(s)


def grid_valores(d: dict) -> str:
    final = d["historia"][str(d["iteraciones"])]
    return (f'<svg class="diagram" viewBox="0 0 500 380" role="img" aria-label="El mundo de 4×3 con el valor de cada casilla y la '
            f'mejor acción: la casilla de salida vale {num(final["1,1"], 3)}">' + _cuadricula(final, d["politica"]) + "</svg>")


def grid_politica(d: dict) -> str:
    return ('<svg class="diagram" viewBox="0 0 500 380" role="img" aria-label="La política óptima del mundo de 4×3: una flecha '
            'en cada casilla; desde la salida sube por la izquierda y llega al +1 por arriba">' + _cuadricula(None, d["politica"]) + "</svg>")


def grid_iteraciones(d: dict) -> str:
    claves = sorted(d["historia"], key=int)
    grupos = []
    for i, k in enumerate(claves):
        clase = "fragment current-visible" if i < len(claves) - 1 else "fragment"
        if i == 0:
            clase = "fragment current-visible"
        grupos.append(f'<g class="{clase}" data-fragment-index="{i}">' + _cuadricula(d["historia"][k], {}, flechas=False)
                      + f'<text x="250" y="398" text-anchor="middle" class="cl" fill="{AMBAR}">iteración {k}</text></g>')
    vacio = _cuadricula({f"{c},{f}": 0.0 for c in (1, 2, 3, 4) for f in (1, 2, 3)}, {}, flechas=False)
    return (f'<svg class="diagram" viewBox="0 0 500 410" role="img" aria-label="La iteración de valores en el mundo de 4×3: los valores '
            f'parten de cero y se propagan desde la salida +1; en la iteración {claves[-1]} ya no cambian">'
            f'<g class="fragment fade-out" data-fragment-index="0">{vacio}<text x="250" y="398" text-anchor="middle" class="cl" fill="{AMBAR}">iteración 0</text></g>'
            + "".join(grupos) + "</svg>")


def grid_recompensas(d: dict) -> str:
    nombres = {"-0.04": ("−0,04", "la del libro"), "-0.2": ("−0,2", "toma el atajo junto al −1"),
               "-2.0": ("−2", "se lanza a cualquier salida"), "0.2": ("+0,2", "evita las salidas: no termina")}
    tarjetas = []
    for i, (r, (rot, efecto)) in enumerate(nombres.items()):
        p = d["recompensas_por_paso"][r]
        clase = " fragment" if i else ""
        nota = " · descuento 0,9" if p["gamma"] != 1.0 else ""
        tarjetas.append(f'<div class="card{clase}" style="padding:8px"><svg viewBox="0 0 340 260" role="img" aria-label="Política con '
                        f'recompensa por paso {rot}: {efecto}">' + _cuadricula(None, p["politica"], celda=80, tam_valor=14) + "</svg>"
                        f'<p style="margin:6px 0 0;font-size:19px;line-height:1.3"><b>{rot}</b>{nota}<br>{efecto}</p></div>')
    return f'<div class="cols" style="grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-top:20px">{"".join(tarjetas)}</div>'


def qlearning(d: dict) -> str:
    q = d["q_learning"]
    vi = d["historia"][str(d["iteraciones"])]["1,1"]
    n = len(q)
    x0, y0, ancho, alto, ymin, ymax = 90, 20, 760, 250, -1.5, 1.0
    ys = lambda v: y0 + alto * (1 - (v - ymin) / (ymax - ymin))
    s = [f'<line x1="{x0}" y1="{y0 + alto}" x2="{x0 + ancho}" y2="{y0 + alto}" stroke="{LINEA}"/>']
    for v in (-1.5, -1.0, -0.5, 0.0, 0.5, 1.0):
        s.append(f'<text x="{x0 - 8}" y="{ys(v) + 5:.0f}" text-anchor="end" class="cs">{num(v, 1)}</text>'
                 f'<line x1="{x0}" y1="{ys(v):.0f}" x2="{x0 + ancho}" y2="{ys(v):.0f}" stroke="#1c2538"/>')
    for i, p in enumerate(q):
        if p["episodio"] % 500 == 0:
            s.append(f'<text x="{x0 + ancho * i / (n - 1):.0f}" y="{y0 + alto + 22}" text-anchor="middle" class="cs">{p["episodio"]}</text>')
    s.append(f'<text x="{x0 + ancho / 2}" y="{y0 + alto + 46}" text-anchor="middle" class="cs">episodios de práctica</text>'
             f'<line x1="{x0}" y1="{ys(vi):.0f}" x2="{x0 + ancho}" y2="{ys(vi):.0f}" stroke="{VERDE}" stroke-dasharray="6 5" stroke-width="2"/>'
             f'<text x="{x0 + 8}" y="{ys(vi) - 8:.0f}" class="cl" fill="{VERDE}">lo que promete la iteración de valores desde la salida: {num(vi, 3)}</text>'
             f'<polyline points="{_linea([p["retorno_medio"] for p in q], x0, y0, ancho, alto, ymin, ymax, n)}" fill="none" stroke="{AMBAR}" stroke-width="3"/>'
             f'<text x="{x0 + ancho - 4}" y="{ys(q[-1]["retorno_medio"]) + 26:.0f}" text-anchor="end" class="cl" fill="{AMBAR}">retorno medio del agente · {num(q[-1]["retorno_medio"], 2)}</text>')
    return (f'<svg class="diagram" viewBox="0 0 900 330" role="img" aria-label="Retorno medio del agente que aprende en el mundo de 4×3, '
            f'de {num(q[0]["retorno_medio"], 2)} a {num(q[-1]["retorno_medio"], 2)} en {q[-1]["episodio"]} episodios">' + ESTILO + "".join(s) + "</svg>")


def qlearning_coincide(d: dict) -> str:
    q = d["q_learning"][-1]
    miles = f"{q['episodio']:,}".replace(",", " ")
    return f"Después de {miles} episodios, su política coincide con la de la iteración de valores en {q['igual_a_iteracion_de_valores']} de 9 casillas."


# ---------------------------------------------------------------- charla de cierre: lo que mostraron los laboratorios

def lab_bote(d: dict) -> str:
    b = d["bote"]
    filas = [("Dar vueltas a la pista", b["vuelta"]), ("Ir y venir sobre una flecha", b["ida_y_vuelta"]),
             ("Lo que aprendió el agente", b["agente"])]
    cuerpo = "".join(f'<tr><td>{a}</td><td>{v["recompensa"]}</td><td{" class=hi" if v["desempeno"] == 0 and i == 2 else ""}>{v["desempeno"]}</td></tr>'
                     for i, (a, v) in enumerate(filas))
    return f'<table class="tbl num"><tr><th>En 100 movimientos</th><th>Recompensa</th><th>Desempeño real</th></tr>{cuerpo}</table>'


def lab_arbol(d: dict) -> str:
    t, c = d["titanic"], d["credito"]
    p = {q["profundidad"]: q for q in t["profundidades"]}
    filas = [("Titanic · regla «mujeres y niños primero»", pct(t["regla_experto"])),
             ("Titanic · árbol de profundidad 3", pct(p[3]["validacion_cruzada"])),
             ("Titanic · bosque aleatorio", pct(t["ensambles"]["bosque aleatorio"]["validacion_cruzada"])),
             (f"German Credit · umbral 0,5: costo {c['umbral_0_5']['costo']}", pct(c["umbral_0_5"]["exactitud"])),
             (f"German Credit · umbral 1/6: costo {c['umbral_costo']['costo']}", pct(c["umbral_costo"]["exactitud"]))]
    cuerpo = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in filas)
    return f'<table class="tbl num"><tr><th>Laboratorio 6A</th><th>Aciertos</th></tr>{cuerpo}</table>'


GRAFICAS = {
    "charla1_del_dato_al_conocimiento.html": {
        "clima_tabla": lambda: clima_tabla(leer("arboles_6a.json")),
        "clima_ganancias": lambda: clima_ganancias(leer("arboles_6a.json")),
        "titanic_arbol": lambda: titanic_arbol(leer("arboles_6a.json")),
        "regla_experto": lambda: regla_experto(leer("arboles_6a.json")),
        "arbol3_cv": lambda: arbol3_cv(leer("arboles_6a.json")),
        "titanic_profundidad": lambda: titanic_profundidad(leer("arboles_6a.json")),
        "titanic_ensambles": lambda: titanic_ensambles(leer("arboles_6a.json")),
        "titanic_pliegues": lambda: titanic_pliegues(leer("arboles_6a.json")),
        "credito_curva": lambda: credito_curva(leer("arboles_6a.json")),
        "hongos": lambda: hongos(leer("arboles_6a.json")),
    },
    "charla2_el_agente_que_aprende_por_refuerzo.html": {
        "grid_politica": lambda: grid_politica(leer("refuerzo_6b.json")),
        "grid_valores": lambda: grid_valores(leer("refuerzo_6b.json")),
        "grid_iteraciones": lambda: grid_iteraciones(leer("refuerzo_6b.json")),
        "grid_recompensas": lambda: grid_recompensas(leer("refuerzo_6b.json")),
        "qlearning": lambda: qlearning(leer("refuerzo_6b.json")),
        "qlearning_coincide": lambda: qlearning_coincide(leer("refuerzo_6b.json")),
    },
    "charla3_aprender_en_los_sistemas_inteligentes_y_cierre.html": {
        "lab_arbol": lambda: lab_arbol(leer("arboles_6a.json")),
        "lab_bote": lambda: lab_bote(leer("refuerzo_6b.json")),
    },
}


def main() -> None:
    for archivo, graficas in GRAFICAS.items():
        ruta = SESION / archivo
        if not ruta.exists():
            print(f"(no existe {archivo})")
            continue
        html = ruta.read_text(encoding="utf-8")
        for nombre, hacer in graficas.items():
            patron = re.compile(rf"(<!--DATOS:{nombre}-->).*?(<!--/DATOS:{nombre}-->)", re.S)
            if not patron.search(html):
                print(f"  falta el marcador {nombre} en {archivo}")
                continue
            html = patron.sub(lambda m: m.group(1) + hacer() + m.group(2), html)
            print(f"  {archivo}: {nombre}")
        ruta.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
