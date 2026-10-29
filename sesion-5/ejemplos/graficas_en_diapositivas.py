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


def leer(nombre: str) -> dict:
    return json.loads((SALIDAS / nombre).read_text(encoding="utf-8"))


def num(x: float, dec: int = 2) -> str:
    return f"{x:.{dec}f}".replace(".", ",")


def pct(x: float, dec: int = 1) -> str:
    return num(100 * x, dec) + " %"


# ---------- Charla inicial ----------

def curva(puntos, x0, y0, ancho, alto, epocas, ymax) -> str:
    paso = max(1, len(puntos) // 150)
    pares = [(i, v) for i, v in enumerate(puntos) if i % paso == 0 or i == len(puntos) - 1]
    return " ".join(f"{x0 + ancho * i / (epocas - 1):.1f},{y0 + alto * (1 - min(v, ymax) / ymax):.1f}" for i, v in pares)


def ejes(x0, y0, ancho, alto, epocas, ymax) -> str:
    s = [f'<line x1="{x0}" y1="{y0 + alto}" x2="{x0 + ancho}" y2="{y0 + alto}" stroke="#2a3550"/>',
         f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + alto}" stroke="#2a3550"/>']
    for e in range(0, epocas + 1, 50):
        x = x0 + ancho * e / epocas
        s.append(f'<text x="{x:.0f}" y="{y0 + alto + 22}" text-anchor="middle" class="cs">{e}</text>')
    for k in range(0, 5):
        v = ymax * k / 4
        y = y0 + alto * (1 - k / 4)
        s.append(f'<text x="{x0 - 8}" y="{y + 5:.0f}" text-anchor="end" class="cs">{num(v, 1)}</text>')
        if k:
            s.append(f'<line x1="{x0}" y1="{y:.0f}" x2="{x0 + ancho}" y2="{y:.0f}" stroke="#1c2538"/>')
    s.append(f'<text x="{x0 + ancho / 2}" y="{y0 + alto + 46}" text-anchor="middle" class="cs">época de entrenamiento</text>')
    s.append(f'<text x="{x0 - 52}" y="{y0 + alto / 2}" text-anchor="middle" class="cs" transform="rotate(-90 {x0 - 52} {y0 + alto / 2})">pérdida (error)</text>')
    return "".join(s)


def grafica_sobreajuste(d: dict) -> str:
    sin = d["sin_regularizacion"]
    x0, y0, ancho, alto, ep, ymax = 90, 20, 760, 300, d["epocas"], 0.8
    xp = x0 + ancho * (sin["parada_temprana"] - 1) / (ep - 1)
    return (f'<svg class="diagram" viewBox="0 0 900 400" role="img" aria-label="Curvas de pérdida de una red grande entrenada con 400 registros del AI4I 2020: la de entrenamiento baja hasta casi cero y la de validación llega a su mínimo de {num(sin["validacion_minima"], 3)} en la época {sin["parada_temprana"]} y después sube hasta {num(sin["validacion_final"], 3)}">'
            '<style>.cs{font-size:15px;fill:#a3adc2}.cl{font-size:17px;font-weight:700}</style>'
            + ejes(x0, y0, ancho, alto, ep, ymax)
            + f'<polyline points="{curva(sin["entrenamiento"], x0, y0, ancho, alto, ep, ymax)}" fill="none" stroke="{CIAN}" stroke-width="3"/>'
            f'<text x="{x0 + ancho - 4}" y="{y0 + alto - 10}" text-anchor="end" class="cl" fill="{CIAN}">entrenamiento</text>'
            f'<g class="fragment"><polyline points="{curva(sin["validacion"], x0, y0, ancho, alto, ep, ymax)}" fill="none" stroke="{AMBAR}" stroke-width="3"/>'
            f'<text x="{x0 + ancho - 4}" y="{y0 + alto * (1 - sin["validacion_final"] / ymax) - 12:.0f}" text-anchor="end" class="cl" fill="{AMBAR}">validación</text></g>'
            f'<g class="fragment"><line x1="{xp:.0f}" y1="{y0}" x2="{xp:.0f}" y2="{y0 + alto}" stroke="{VERDE}" stroke-dasharray="6 5" stroke-width="2"/>'
            f'<text x="{xp + 8:.0f}" y="{y0 + 18}" class="cl" fill="{VERDE}">aquí empieza a memorizar (época {sin["parada_temprana"]})</text></g>'
            '</svg>')


def grafica_dropout(d: dict) -> str:
    sin, con = d["sin_regularizacion"], d["con_dropout"]
    x0, y0, ancho, alto, ep, ymax = 90, 20, 760, 300, d["epocas"], 0.5
    xp = x0 + ancho * (con["parada_temprana"] - 1) / (ep - 1)
    return (f'<svg class="diagram" viewBox="0 0 900 400" role="img" aria-label="Pérdida de validación sin regularización, que termina en {num(sin["validacion_final"], 3)}, y con dropout del 30 %, que termina en {num(con["validacion_final"], 3)}; la parada temprana se queda con la época {con["parada_temprana"]}, con pérdida {num(con["validacion_minima"], 3)}">'
            '<style>.cs{font-size:15px;fill:#a3adc2}.cl{font-size:17px;font-weight:700}</style>'
            + ejes(x0, y0, ancho, alto, ep, ymax)
            + f'<polyline points="{curva(sin["validacion"], x0, y0, ancho, alto, ep, ymax)}" fill="none" stroke="{AMBAR}" stroke-width="3" stroke-dasharray="7 5"/>'
            f'<text x="{x0 + ancho - 4}" y="{y0 + alto * (1 - sin["validacion_final"] / ymax) - 12:.0f}" text-anchor="end" class="cl" fill="{AMBAR}">validación sin regularizar · {num(sin["validacion_final"], 2)}</text>'
            f'<g class="fragment"><polyline points="{curva(con["validacion"], x0, y0, ancho, alto, ep, ymax)}" fill="none" stroke="{VERDE}" stroke-width="3"/>'
            f'<text x="{x0 + ancho - 4}" y="{y0 + alto * (1 - con["validacion_final"] / ymax) + 26:.0f}" text-anchor="end" class="cl" fill="{VERDE}">con dropout · {num(con["validacion_final"], 2)}</text></g>'
            f'<g class="fragment"><line x1="{xp:.0f}" y1="{y0}" x2="{xp:.0f}" y2="{y0 + alto}" stroke="{CIAN}" stroke-dasharray="6 5" stroke-width="2"/>'
            f'<text x="{xp + 8:.0f}" y="{y0 + 18}" class="cl" fill="{CIAN}">parada temprana: época {con["parada_temprana"]} · {num(con["validacion_minima"], 2)}</text></g>'
            '</svg>')


def color_calor(v: float, vmin: float, vmax: float, base=(56, 189, 248)) -> str:
    t = 0 if vmax == vmin else max(0.0, min(1.0, (v - vmin) / (vmax - vmin)))
    fondo = (23, 32, 51)
    r, g, b = (round(f + t * (c - f)) for f, c in zip(fondo, base))
    return f"rgb({r},{g},{b})"


def matriz_confusion(d: dict) -> str:
    m = d["matriz_confusion"]
    filas = ['<tr><th>real ↓ · leído →</th>' + "".join(f"<th>{k}</th>" for k in range(10)) + "</tr>"]
    for r in range(10):
        celdas = []
        for p in range(10):
            v = m[r][p]
            if r == p:
                estilo = f"background:{color_calor(v, 800, 1150, (74, 222, 128))}"
            elif v:
                estilo = f"background:{color_calor(v, 0, 20, (248, 113, 113))};color:#e8ecf4"
            else:
                estilo = "background:#111827;color:#2a3550"
            celdas.append(f'<td style="{estilo}">{v}</td>')
        filas.append(f"<tr><th>{r}</th>{''.join(celdas)}</tr>")
    return '<table class="heat sm">' + "".join(filas) + "</table>"


def resumen_cnn(d: dict) -> str:
    pares = "; ".join(f'{c["real"]} leído como {c["leido_como"]} ({c["veces"]} veces)' for c in d["mas_confundidos"][:3])
    miles = lambda x: f"{x:,}".replace(",", ".")
    return (f'<p class="big-number" style="font-size:56px;margin:0">{pct(d["exactitud_prueba"], 1)}</p>'
            f'<p class="small muted" style="margin-top:0">de las {miles(d["imagenes_prueba"])} imágenes de prueba, que la red nunca vio. '
            f'{d["epocas"]} épocas, {d["segundos_entrenamiento"]} s en un portátil, {miles(d["parametros"])} parámetros.</p>'
            f'<p class="small" style="margin-top:4px">Lo que más confunde: {pares}.</p>')


# ---------- Charla intermedia ----------

def fichas(piezas: list[str]) -> str:
    return "".join(f"<span>{escape(p) if p.strip() else '␣'}</span>" for p in piezas) + f'<span class="n">{len(piezas)} tokens</span>'


def tokens(d: dict) -> str:
    t = d["tokens"]
    filas = [("GPT-2 · español", "gpt2_es"), ("GPT-2 · inglés", "gpt2_en"),
             ("Qwen2.5 · español", "qwen2.5_es"), ("Qwen2.5 · inglés", "qwen2.5_en")]
    partes = []
    for i, (titulo, clave) in enumerate(filas):
        clase = ' class="fragment"' if i == 2 else ""
        if i == 2:
            partes.append(f"<div{clase}>")
        partes.append(f'<div class="toklbl">{titulo}</div><div class="tokens">{fichas(t[clave])}</div>')
    partes.append("</div>")
    return "".join(partes)


def tabla_conteo(d: dict) -> str:
    t = d["tokens"]
    n = {k: len(v) for k, v in t.items()}
    return ('<table class="tbl num"><tr><th>Tokenizador</th><th>Español</th><th>Inglés</th><th>El español cuesta</th></tr>'
            f'<tr><td>GPT-2 (2019, entrenado en inglés)</td><td>{n["gpt2_es"]}</td><td>{n["gpt2_en"]}</td><td class="hi">{num(n["gpt2_es"] / n["gpt2_en"], 1)} veces</td></tr>'
            f'<tr><td>Qwen2.5 (2024, multilingüe)</td><td>{n["qwen2.5_es"]}</td><td>{n["qwen2.5_en"]}</td><td class="hi">{num(n["qwen2.5_es"] / n["qwen2.5_en"], 1)} veces</td></tr></table>')


def similitud_banco(d: dict) -> str:
    b = d["banco"]
    etiquetas = ["pagar en el banco", "crédito en el banco", "se sentó en el banco", "descansar en el banco"]

    def tabla(m, titulo):
        filas = ['<tr><th></th>' + "".join(f"<th>{i + 1}</th>" for i in range(4)) + "</tr>"]
        for i, fila in enumerate(m):
            filas.append(f"<tr><th style=\"text-align:right\">{i + 1} · {etiquetas[i]}</th>"
                         + "".join(f'<td style="background:{color_calor(v, 0.7, 1.0)}">{num(v)}</td>' for v in fila) + "</tr>")
        return f'<div><div class="toklbl">{titulo}</div><table class="heat">{"".join(filas)}</table></div>'
    return (f'<div class="cols" style="gap:28px">{tabla(b["similitud_antes"], "Antes de la primera capa")}'
            f'<div class="fragment">{tabla(b["similitud_capa"], "Después de " + str(b["capa"]) + " capas")}</div></div>')


def atencion(d: dict) -> str:
    a = d["atencion"][1]
    pesos = a["pesos_sin_primer_token"]
    tope = max(pesos)
    filas = []
    for tok, p in zip(a["tokens"], pesos):
        clase = "bar a" if p == tope else "bar"
        filas.append(f'<span class="lb">{escape(tok.strip() or "·")}</span><span class="{clase}" style="width:{100 * p / tope:.0f}%"></span><span class="val">{pct(p, 0)}</span>')
    return f'<div class="toklbl">«…en el banco» · ¿a quién atiende «banco»?</div><div class="bars" style="font-size:19px;gap:3px 10px">{"".join(filas)}</div>'


def barras_siguiente(lista: list, tope: float, clase: str = "bar") -> str:
    filas = [f'<span class="lb">«{escape(x["token"].strip())}…»</span><span class="{clase}" style="width:{100 * x["probabilidad"] / tope:.0f}%"></span><span class="val">{pct(x["probabilidad"])}</span>'
             for x in lista]
    return f'<div class="bars">{"".join(filas)}</div>'


def siguiente_t1(d: dict) -> str:
    s = d["siguiente_token"]
    lista = s["temperaturas"]["1.0"][:6]
    inicio = escape(s["inicio"].split(". ", 1)[1])
    return f'<p class="gen"><span class="t">Entrada</span>…{inicio} <strong>▮</strong></p>' + barras_siguiente(lista, lista[0]["probabilidad"])


def temperatura(d: dict) -> str:
    s = d["siguiente_token"]["temperaturas"]
    tope = s["0.5"][0]["probabilidad"]
    grupos = []
    for i, (t, clase) in enumerate([("0.5", "bar"), ("1.0", "bar v"), ("1.5", "bar a")]):
        frag = ' class="fragment"' if i else ""
        grupos.append(f'<div{frag}><div class="toklbl">Temperatura {t.replace(".", ",")}</div>{barras_siguiente(s[t][:4], tope, clase)}</div>')
    return '<div class="cols-3" style="gap:20px">' + "".join(grupos) + "</div>"


def continuaciones(d: dict) -> str:
    c = d["continuaciones"]
    nombres = {"0.2": "0,2 · se repite", "0.8": "0,8 · plausible", "1.3": "1,3 · sin sentido"}
    filas = []
    for i, (t, textos) in enumerate(c.items()):
        texto = re.sub(r"\s+", " ", textos[0]).strip()
        frag = " fragment" if i else ""
        filas.append(f'<p class="gen{frag}"><span class="t">T = {nombres[t]}</span>…es un {escape(texto)}…</p>')
    return "".join(filas)


# ---------- Charla de cierre ----------

def piloto(d: dict) -> str:
    nombres = {"bolsa de palabras": "Bolsa de palabras (sin orden ni significado)",
               "ibm-granite/granite-embedding-107m-multilingual": "Transformer · Granite (214 MB), el del 5B",
               "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2": "Transformer · MiniLM multilingüe (471 MB)",
               "intfloat/multilingual-e5-small": "Transformer · e5-small multilingüe (471 MB)"}
    filas = ["<tr><th>Representación</th><th>Aciertos</th><th>«Hay fuga» frente a «No hay fuga»</th></tr>"]
    for r in d["resultados"]:
        sim = num(r["similitud_fuga_no_fuga"]) if "similitud_fuga_no_fuga" in r else "—"
        clase = ' class="hi"' if r["representacion"].startswith("ibm") else ""
        filas.append(f'<tr><td>{nombres[r["representacion"]]}</td><td{clase}>{r["aciertos"]} de {d["prueba"]}</td><td>{sim}</td></tr>')
    return f'<table class="tbl num">{"".join(filas)}</table>'


GRAFICAS = {
    "charla1_de_la_neurona_a_la_red_profunda.html": {
        "sobreajuste": lambda: grafica_sobreajuste(leer("curvas_5a.json")),
        "dropout": lambda: grafica_dropout(leer("curvas_5a.json")),
        "cnn_resumen": lambda: resumen_cnn(leer("cnn_mnist.json")),
        "cnn_confusion": lambda: matriz_confusion(leer("cnn_mnist.json")),
    },
    "charla2_la_arquitectura_transformer.html": {
        "tokens": lambda: tokens(leer("modelo_de_lenguaje.json")),
        "atencion": lambda: atencion(leer("modelo_de_lenguaje.json")),
        "banco": lambda: similitud_banco(leer("modelo_de_lenguaje.json")),
        "siguiente": lambda: siguiente_t1(leer("modelo_de_lenguaje.json")),
        "temperatura": lambda: temperatura(leer("modelo_de_lenguaje.json")),
        "continuaciones": lambda: continuaciones(leer("modelo_de_lenguaje.json")),
    },
    "charla3_de_los_transformers_a_los_llms_y_cierre.html": {
        "piloto": lambda: piloto(leer("codificador_5b.json")),
        "conteo": lambda: tabla_conteo(leer("modelo_de_lenguaje.json")),
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
