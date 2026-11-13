"""Pone en las diapositivas las gráficas hechas con los números de salidas/ (córrelo después de los ejemplos).

Cada gráfica va en el HTML entre dos comentarios, <!--DATOS:nombre--> y <!--/DATOS:nombre-->.
El script reemplaza lo que hay entre ellos, así que puedes correrlo las veces que quieras.
Los decimales llevan punto, como pide Especializacion AI/normas.md desde la Sesión 7.
Los SVG usan las clases .dg de tema-si.css, que cambian con el tema claro u oscuro.

Uso, desde esta carpeta:  python graficas_en_diapositivas.py
Solo usa la biblioteca estándar de Python.
"""
import json
import re
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SALIDAS = AQUI / "salidas"
SESION = AQUI.parent


def leer(nombre: str) -> dict:
    return json.loads((SALIDAS / nombre).read_text(encoding="utf-8"))


def num(x: float, dec: int = 2) -> str:
    return f"{x:.{dec}f}"


def pct(x: float, dec: int = 1) -> str:
    return f"{100 * x:.{dec}f} %"


def barras(filas: list, clase_extra: str = "") -> str:
    """Barras horizontales de probabilidad, de 0 a 100 %. Cada fila es (rótulo, valor, clase, ¿fragmento?)."""
    partes = []
    for rotulo, valor, clase, fragmento in filas:
        f = " fragment" if fragmento else ""
        ancho = max(0.4, 100 * valor)
        partes.append(f'<span class="lb{f}">{rotulo}</span><span class="bar {clase}{f}" style="width:{ancho:.1f}%"></span>'
                      f'<span class="val{f}">{pct(valor)}</span>')
    return f'<div class="bars {clase_extra}" style="font-size:22px;gap:10px 14px">{"".join(partes)}</div>'


# ---------------------------------------------------------------- charla inicial

def iconos(d: dict) -> str:
    """El diagrama de iconos: 1000 bombas, las que fallan y las alarmas, en tres pasos."""
    cols, radio, paso = 40, 6.2, 16
    filas = d["bombas"] // cols
    ancho, alto = cols * paso + 10, filas * paso + 10

    def punto(i: int, clase: str) -> str:
        x, y = 5 + paso / 2 + (i % cols) * paso, 5 + paso / 2 + (i // cols) * paso
        return f'<circle class="ic {clase}" cx="{x:.1f}" cy="{y:.1f}" r="{radio}"/>'

    base = "".join(punto(i, "") for i in range(d["bombas"]))
    fallan = "".join(punto(i, "falla") for i in range(d["fallan"]))
    # Las detectadas quedan rellenas; la que no se detecta, solo con borde
    detectadas = "".join(punto(i, "falla") for i in range(d["detectadas"]))
    oculta = "".join(punto(i, "falla-oculta") for i in range(d["detectadas"], d["fallan"]))
    falsas = "".join(punto(i, "falsa") for i in range(d["fallan"], d["fallan"] + d["falsas"]))
    return (f'<svg class="diagram dg" viewBox="0 0 {ancho} {alto}" role="img" aria-label="Diagrama de 1000 círculos, uno por bomba: '
            f'{d["fallan"]} fallan; la alarma avisa en {d["detectadas"]} de ellas y en {d["falsas"]} bombas sanas">'
            f'<g>{base}</g><g class="fragment">{fallan}</g>'
            f'<g class="fragment"><g>{"".join(punto(i, "") for i in range(d["fallan"]))}</g>{detectadas}{oculta}{falsas}</g></svg>')


def iconos_cuenta(d: dict) -> str:
    return (f'<p class="fragment" style="font-size:24px">De <strong>{d["avisos"]} avisos</strong>, solo <strong>{d["detectadas"]}</strong> '
            f'son fallas: <strong>{pct(d["posterior"])}</strong>.</p>')


def creencia_bomba(d: dict) -> str:
    """La creencia en la falla de una bomba, antes y después de la alarma."""
    return barras([("antes de cualquier dato", d["tasa_falla"], "g", False),
                   ("sonó la alarma de vibración", d["posterior"], "bad", True)])


def decision_bomba(d: dict) -> str:
    """La utilidad esperada de esperar o reemplazar, antes y después de la alarma."""
    nombres = {"sin_alarma": "Sin alarma", "con_alarma": "Sonó la alarma"}
    filas = ['<tr><th></th><th>P(falla)</th><th>Esperar</th><th>Reemplazar ya</th><th>Mejor decisión</th></tr>']
    for i, (k, v) in enumerate(d["decision"].items()):
        f = ' class="fragment"' if i else ""
        e_cl = "pos" if v["mejor"] == "esperar" else "neg"
        r_cl = "pos" if v["mejor"] == "reemplazar" else "neg"
        filas.append(f'<tr{f}><td>{nombres[k]}</td><td>{pct(v["p_falla"])}</td>'
                     f'<td class="{e_cl}">{num(v["esperar"], 1)}</td><td class="{r_cl}">{num(v["reemplazar"], 1)}</td>'
                     f'<td>{v["mejor"]}</td></tr>')
    return f'<table class="tbl cuenta">{"".join(filas)}</table>'


def creencia_robo(d: dict) -> str:
    c = d["consultas"]
    return barras([("antes de saber nada", c["robo_previa"], "g", False),
                   ("llama Juan", c["robo_juan"], "", True),
                   ("llaman Juan y María", c["robo_juan_maria"], "bad", True)])


def explicacion(d: dict) -> str:
    c = d["consultas"]
    return barras([("sonó la alarma", c["robo_alarma"], "bad", False),
                   ("sonó y hubo sismo", c["robo_alarma_sismo"], "ok", True),
                   ("sonó y llamó Juan", c["robo_alarma_juan"], "bad", True)])


def prediccion(d: dict) -> str:
    c = d["consultas"]
    return barras([("suena la alarma", c["alarma_robo"], "a", False),
                   ("llama Juan", c["juan_robo"], "a", True),
                   ("llama María", c["maria_robo"], "a", True)])


def petrolero_sin(d: dict) -> str:
    nombres = {"seco": "seco", "humedo": "húmedo", "empapado": "empapado"}
    filas = ['<tr><th>Pozo</th><th>P</th><th>Ganancia</th><th>P × ganancia</th></tr>']
    for p, prob in d["p_pozo"].items():
        g = d["ganancia"][p]
        clase = "neg" if g < 0 else "pos"
        filas.append(f'<tr><td>{nombres[p]}</td><td>{num(prob, 1)}</td><td class="{clase}">{g}</td><td>{num(prob * g, 1)}</td></tr>')
    filas.append(f'<tr class="total"><td colspan="3">Perforar sin la prueba vale</td>'
                 f'<td class="pos">{num(d["a_mano"]["ue_sin_prueba"], 1)}</td></tr>')
    return f'<table class="tbl cuenta">{"".join(filas)}</table>'


def petrolero_valor(d: dict) -> str:
    nombres = {"sin_estructura": "sin estructura", "abierta": "abierta", "cerrada": "cerrada"}
    m = d["a_mano"]
    filas = ['<tr><th>La prueba dice</th><th>P</th><th>Perforar vale</th><th>Decisión</th></tr>']
    for r, v in m["por_resultado"].items():
        clase = "neg" if v["ue_perforar"] < 0 else "pos"
        filas.append(f'<tr class="fragment"><td>{nombres[r]}</td><td>{num(v["p"], 2)}</td>'
                     f'<td class="{clase}">{num(v["ue_perforar"], 1)}</td><td>{v["decision"]}</td></tr>')
    filas.append(f'<tr class="total fragment"><td colspan="2">Con la prueba gratis</td><td class="pos">{num(m["ue_con_prueba_gratis"], 1)}</td>'
                 f'<td>sin ella: {num(m["ue_sin_prueba"], 1)}</td></tr>')
    return f'<table class="tbl cuenta">{"".join(filas)}</table>'


def petrolero_veredicto(d: dict) -> str:
    m = d["a_mano"]
    return (f'<p class="fragment" style="font-size:24px">La prueba vale <strong>{num(m["valor_informacion"], 1)}</strong> '
            f'y cuesta <strong>{d["costo_prueba"]}</strong>: conviene hacerla. Con su precio, la decisión vale '
            f'{num(m["ue_con_prueba_pagada"], 1)}.</p>')


# ---------------------------------------------------------------- charla intermedia

def curva_dominio(d: dict) -> str:
    """La curva de dominio estimado de un técnico simulado, respuesta a respuesta."""
    e = d["ejemplo"]
    curva, resp = e["curva"], e["respuestas"]
    x0, y0, ancho, alto = 70, 20, 760, 300
    paso = ancho / (len(curva) - 1)

    def px(i):
        return x0 + i * paso

    def py(v):
        return y0 + alto * (1 - v)

    partes = [f'<line class="rejilla" x1="{x0}" y1="{py(v):.1f}" x2="{x0 + ancho}" y2="{py(v):.1f}"/>'
              f'<text class="t3" x="{x0 - 10}" y="{py(v) + 5:.1f}" text-anchor="end">{num(v, 1)}</text>' for v in (0, 0.5, 1)]
    partes.append(f'<line class="umbral" x1="{x0}" y1="{py(d["umbral"]):.1f}" x2="{x0 + ancho}" y2="{py(d["umbral"]):.1f}"/>'
                  f'<text class="t2" x="{x0 + 8}" y="{py(d["umbral"]) - 8:.1f}">umbral de dominio: {d["umbral"]}</text>')
    partes.append(f'<circle class="c-accent" cx="{px(0):.1f}" cy="{py(curva[0]):.1f}" r="6"/>'
                  f'<text class="t2" x="{px(0):.1f}" y="{y0 + alto + 52}" text-anchor="middle">inicio</text>')
    for i, r in enumerate(resp, start=1):
        marca = '<tspan class="c-ok">✓</tspan>' if r else '<tspan class="c-bad">✗</tspan>'
        partes.append(f'<g class="fragment"><line class="curva" x1="{px(i - 1):.1f}" y1="{py(curva[i - 1]):.1f}" x2="{px(i):.1f}" y2="{py(curva[i]):.1f}"/>'
                      f'<circle class="c-accent" cx="{px(i):.1f}" cy="{py(curva[i]):.1f}" r="6"/>'
                      f'<text class="tn" x="{px(i):.1f}" y="{py(curva[i]) - 14:.1f}" text-anchor="middle">{num(curva[i], 2)}</text>'
                      f'<text x="{px(i):.1f}" y="{y0 + alto + 30}" text-anchor="middle" style="font-size:24px;font-weight:800">{marca}</text>'
                      f'<text class="t3" x="{px(i):.1f}" y="{y0 + alto + 52}" text-anchor="middle">{i}</text></g>')
    return (f'<svg class="diagram dg" viewBox="0 0 860 390" role="img" aria-label="Curva del dominio estimado de un técnico simulado: '
            f'empieza en {num(curva[0], 2)} y, con {len(resp)} respuestas, llega a {num(curva[-1], 2)}, por encima del umbral de {d["umbral"]}">'
            f'<line class="eje" x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + alto}"/>{"".join(partes)}</svg>')


def parametros(d: dict) -> str:
    """Los cuatro parámetros de la habilidad del ejemplo, en lenguaje de negocio."""
    h = d["habilidades"][d["ejemplo"]["habilidad"]]
    tarjetas = [("accent", "Dominio inicial", "P(L₀)", h["L0"], "con qué dominio llega el técnico"),
                ("ok", "Aprendizaje", "P(T)", h["T"], "cuánto aprende en cada práctica"),
                ("amber", "Adivinanza", "P(G)", h["G"], "cuánto acierta sin dominar"),
                ("violet", "Descuido", "P(S)", h["S"], "cuánto falla aunque domine")]
    partes = []
    for i, (color, titulo, simbolo, valor, texto) in enumerate(tarjetas):
        f = " fragment" if i else ""
        partes.append(f'<div class="card {color}{f}"><h4>{titulo}</h4><p style="font-size:30px;font-weight:800;margin:2px 0">{num(valor, 2)}</p>'
                      f'<p style="font-size:18px;margin:0">{texto} · <span class="mono">{simbolo}</span></p></div>')
    return f'<div class="cols-4">{"".join(partes)}</div><p class="toklbl" style="margin-top:10px">Habilidad del ejemplo: {h["nombre"]}</p>'


def reglas_dominio(d: dict) -> str:
    filas = [f'<tr><th>Habilidad</th><th>Hasta dominar ({d["umbral"]})</th><th>Siempre {d["fijo"]} ejercicios</th></tr>']
    for h in d["habilidades"].values():
        dom, fijo = h["reglas"]["dominio"], h["reglas"]["fijo"]
        filas.append(f'<tr><td>{h["nombre"]}</td>'
                     f'<td class="pos">{pct(dom["dominan_al_terminar"], 0)} dominan · {num(dom["ejercicios_promedio"], 1)} ejercicios</td>'
                     f'<td class="neg">{pct(fijo["dominan_al_terminar"], 0)} dominan</td></tr>')
    return f'<table class="tbl cuenta">{"".join(filas)}</table>'


# ---------------------------------------------------------------- charla de cierre

def confusion(d: dict) -> str:
    t, tot = d["tasas_por_edad"], d["total"]
    filas = ['<tr><th></th><th>Mantenimiento frecuente</th><th>Poco mantenimiento</th></tr>',
             f'<tr><td><strong>Todas las bombas</strong></td><td class="neg">{pct(tot["frecuente"]["tasa"], 0)} fallan</td>'
             f'<td class="pos">{pct(tot["poco"]["tasa"], 0)} fallan</td></tr>',
             f'<tr class="fragment"><td>Bombas nuevas</td><td class="pos">{pct(t["nuevas"]["frecuente"], 0)}</td><td class="neg">{pct(t["nuevas"]["poco"], 0)}</td></tr>',
             f'<tr class="fragment"><td>Bombas viejas</td><td class="pos">{pct(t["viejas"]["frecuente"], 0)}</td><td class="neg">{pct(t["viejas"]["poco"], 0)}</td></tr>']
    return f'<table class="tbl cuenta">{"".join(filas)}</table>'


def laboratorios(d_alarma: dict, d_petrolero: dict, d_bkt: dict) -> str:
    c, m = d_alarma["consultas"], d_petrolero["a_mano"]
    h = d_bkt["habilidades"]["alineacion"]["reglas"]
    return ('<div class="cols-3">'
            f'<div class="card accent"><h4>Red de la alarma</h4><p>Con las dos llamadas, el robo pasa de {pct(c["robo_previa"])} a '
            f'<strong>{pct(c["robo_juan_maria"])}</strong>.</p></div>'
            f'<div class="card amber fragment"><h4>El petrolero</h4><p>La prueba vale <strong>{num(m["valor_informacion"], 1)}</strong> '
            f'y cuesta {d_petrolero["costo_prueba"]}: conviene probar.</p></div>'
            f'<div class="card ok fragment"><h4>El tutor</h4><p>Con la regla de dominio, el {pct(h["dominio"]["dominan_al_terminar"], 0)} '
            f'domina; con {d_bkt["fijo"]} ejercicios fijos, el {pct(h["fijo"]["dominan_al_terminar"], 0)}.</p></div></div>')


GRAFICAS = {
    "charla1_creer_con_evidencia_y_decidir.html": {
        "iconos": lambda: iconos(leer("tasa_base_7a.json")),
        "iconos_cuenta": lambda: iconos_cuenta(leer("tasa_base_7a.json")),
        "decision_bomba": lambda: decision_bomba(leer("tasa_base_7a.json")),
        "creencia_bomba": lambda: creencia_bomba(leer("tasa_base_7a.json")),
        "creencia_robo": lambda: creencia_robo(leer("alarma_7a.json")),
        "prediccion": lambda: prediccion(leer("alarma_7a.json")),
        "explicacion": lambda: explicacion(leer("alarma_7a.json")),
        "petrolero_sin": lambda: petrolero_sin(leer("petrolero_7a.json")),
        "petrolero_valor": lambda: petrolero_valor(leer("petrolero_7a.json")),
        "petrolero_veredicto": lambda: petrolero_veredicto(leer("petrolero_7a.json")),
    },
    "charla2_el_tutor_que_estima_lo_que_sabes.html": {
        "parametros": lambda: parametros(leer("bkt_7b.json")),
        "curva_dominio": lambda: curva_dominio(leer("bkt_7b.json")),
        "reglas_dominio": lambda: reglas_dominio(leer("bkt_7b.json")),
    },
    "charla3_decidir_bajo_incertidumbre_y_cierre.html": {
        "laboratorios": lambda: laboratorios(leer("alarma_7a.json"), leer("petrolero_7a.json"), leer("bkt_7b.json")),
        "confusion": lambda: confusion(leer("confusion_7.json")),
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
