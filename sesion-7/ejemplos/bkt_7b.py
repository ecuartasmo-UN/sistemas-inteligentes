"""Bayesian Knowledge Tracing con técnicos simulados (charla intermedia y Laboratorio 7B).

El curso: la inducción de los técnicos nuevos de MantenIA, una empresa ficticia.
Tiene tres habilidades. Cada técnico practica ejercicios y acierta o falla.
Los datos salen de una simulación con parámetros conocidos: no hay personas reales.

El script hace tres cosas:
- simula las respuestas de 200 técnicos por habilidad, con la semilla 7;
- estima el dominio de cada técnico, respuesta a respuesta, con las ecuaciones de Corbett y Anderson (1994);
- compara dos reglas para elegir el siguiente ejercicio: practicar hasta que el dominio estimado
  supere 0.95, o hacer siempre el mismo número de ejercicios.

Uso, desde esta carpeta:  python bkt_7b.py
Requiere numpy. Escribe salidas/bkt_7b.json.
"""
import numpy as np

from comun import guardar_json, red

SEMILLA = 7
TECNICOS = 200          # técnicos simulados por habilidad
UMBRAL = 0.95           # el dominio estimado con el que se pasa a la siguiente habilidad
MAX_EJERCICIOS = 30     # tope de ejercicios por habilidad
FIJO = 5                # la regla alternativa: siempre 5 ejercicios por habilidad

# Los cuatro parámetros de cada habilidad: dominio inicial, aprendizaje, adivinanza y descuido
HABILIDADES = {
    "bloqueo": {"nombre": "Bloqueo y etiquetado", "L0": 0.30, "T": 0.20, "G": 0.20, "S": 0.08},
    "alineacion": {"nombre": "Alineación de una bomba", "L0": 0.10, "T": 0.12, "G": 0.15, "S": 0.10},
    "vibracion": {"nombre": "Lectura de vibración", "L0": 0.15, "T": 0.15, "G": 0.25, "S": 0.10},
}


def actualizar(p: float, acierto: bool, h: dict) -> float:
    """Una respuesta: primero la regla de Bayes, después la oportunidad de aprender."""
    if acierto:
        post = p * (1 - h["S"]) / (p * (1 - h["S"]) + (1 - p) * h["G"])
    else:
        post = p * h["S"] / (p * h["S"] + (1 - p) * (1 - h["G"]))
    return post + (1 - post) * h["T"]


def simular_tecnico(h: dict, rng: np.random.Generator, regla: str):
    """Simula a un técnico hasta que la regla diga «basta». Devuelve sus respuestas, la curva y si domina."""
    domina = rng.random() < h["L0"]           # el estado oculto: ¿ya domina la habilidad?
    p = h["L0"]                                # lo que estima el tutor
    respuestas, curva = [], [p]
    while len(respuestas) < MAX_EJERCICIOS:
        if regla == "dominio" and p >= UMBRAL:
            break
        if regla == "fijo" and len(respuestas) >= FIJO:
            break
        acierto = rng.random() < ((1 - h["S"]) if domina else h["G"])
        respuestas.append(bool(acierto))
        p = actualizar(p, acierto, h)
        curva.append(p)
        if not domina and rng.random() < h["T"]:   # practicar puede enseñar
            domina = True
    return respuestas, curva, domina


def main() -> None:
    rng = np.random.default_rng(SEMILLA)
    resultados = {}
    for clave, h in HABILIDADES.items():
        por_regla = {}
        for regla in ("dominio", "fijo"):
            ejercicios, dominan = [], 0
            for _ in range(TECNICOS):
                resp, _, domina = simular_tecnico(h, rng, regla)
                ejercicios.append(len(resp))
                dominan += domina
            por_regla[regla] = {"ejercicios_promedio": red(np.mean(ejercicios), 2),
                                "ejercicios_min": int(min(ejercicios)), "ejercicios_max": int(max(ejercicios)),
                                "dominan_al_terminar": red(dominan / TECNICOS, 3)}
        resultados[clave] = {**h, "reglas": por_regla}
        d, f = por_regla["dominio"], por_regla["fijo"]
        print(f"{h['nombre']:24} dominio ≥ {UMBRAL}: {d['ejercicios_promedio']:5.2f} ejercicios, "
              f"{d['dominan_al_terminar']:.1%} dominan · fijo {FIJO}: {f['dominan_al_terminar']:.1%} dominan")

    # Un técnico de ejemplo para la curva de la charla: el primero, con la semilla 7,
    # cuya secuencia tiene un error después de un acierto y llega al umbral en 6 a 10 ejercicios.
    rng = np.random.default_rng(SEMILLA)
    h = HABILIDADES["alineacion"]
    for indice in range(1000):
        resp, curva, _ = simular_tecnico(h, rng, "dominio")
        errores_tardios = any(resp[i] and not resp[i + 1] for i in range(len(resp) - 1))
        if 6 <= len(resp) <= 10 and errores_tardios and curva[-1] >= UMBRAL:
            break
    print(f"Técnico de ejemplo (número {indice}): {['✓' if r else '✗' for r in resp]}")
    print("Dominio estimado:", " ".join(f"{c:.2f}" for c in curva))

    # La regla de selección entre habilidades, para un técnico: practicar la de menor dominio estimado
    rng = np.random.default_rng(SEMILLA + 1)
    estimado = {k: v["L0"] for k, v in HABILIDADES.items()}
    oculto = {k: rng.random() < v["L0"] for k, v in HABILIDADES.items()}
    secuencia = []
    while min(estimado.values()) < UMBRAL and len(secuencia) < 3 * MAX_EJERCICIOS:
        k = min(estimado, key=estimado.get)
        hk = HABILIDADES[k]
        acierto = rng.random() < ((1 - hk["S"]) if oculto[k] else hk["G"])
        estimado[k] = actualizar(estimado[k], acierto, hk)
        if not oculto[k] and rng.random() < hk["T"]:
            oculto[k] = True
        secuencia.append({"habilidad": k, "acierto": bool(acierto), "estimado": red(estimado[k], 3)})
    print(f"Selección entre habilidades: {len(secuencia)} ejercicios hasta dominar las tres.")

    guardar_json("bkt_7b.json", {
        "semilla": SEMILLA, "tecnicos": TECNICOS, "umbral": UMBRAL, "fijo": FIJO, "max_ejercicios": MAX_EJERCICIOS,
        "habilidades": resultados,
        "ejemplo": {"habilidad": "alineacion", "indice": indice, "respuestas": resp, "curva": [red(c, 3) for c in curva]},
        "seleccion": secuencia})


if __name__ == "__main__":
    main()
