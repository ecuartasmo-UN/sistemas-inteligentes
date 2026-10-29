"""La prueba que eligió el modelo del Laboratorio 5B (charla de cierre, «Lo que mostró el 5B»).

Doce órdenes de trabajo de MantenIA, tres por equipo, sirven de ejemplos; dieciséis órdenes nuevas,
escritas con otras palabras, son la prueba. Cada orden nueva va al equipo cuyo promedio de ejemplos
se parece más (el centroide), con cuatro representaciones:
- una bolsa de palabras: cuenta las palabras, sin orden ni significado;
- tres codificadores multilingües preentrenados (transformers), sin ajustarlos.
Además mide cuánto se parecen «Hay fuga de aceite en la bomba 3» y su negación.

Uso, desde esta carpeta:  python codificador_5b.py
Requiere sentence-transformers. La primera vez descarga los tres codificadores (214 + 471 + 471 MB).
Escribe los números en salidas/codificador_5b.json.
"""
import re
from collections import Counter

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from comun import guardar_json

CODIFICADORES = [  # (modelo, commit, prefijo que pide el modelo)
    ("ibm-granite/granite-embedding-107m-multilingual", "d6cffd338414d6a1c1f5decfad5fec62eebc90d5", ""),
    ("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", None, ""),
    ("intfloat/multilingual-e5-small", None, "query: "),
]
EJEMPLOS = {
    "eléctrico": ["El motor del compresor no arranca y salta el breaker", "Tablero de la línea 2 sin energía",
                  "Cable quemado en la caja de conexiones del ventilador"],
    "mecánico": ["Rodamiento de la bomba 3 con ruido y vibración alta", "Correa de la banda transportadora desgastada",
                 "Eje del agitador desalineado"],
    "fugas": ["Fuga de aceite en la caja reductora", "Goteo de agua en la válvula de entrada",
              "Pérdida de presión por fuga en la manguera hidráulica"],
    "instrumentación": ["El sensor de temperatura marca valores erráticos", "Manómetro de la caldera descalibrado",
                        "El transmisor de nivel no envía señal al PLC"],
}
PRUEBA = {
    "eléctrico": ["Se dispara el interruptor cada vez que encendemos la máquina", "No llega corriente al equipo de la zona de empaque",
                  "Olor a quemado en el cuadro eléctrico", "Corto circuito en la alimentación del horno"],
    "mecánico": ["Golpeteo metálico en la transmisión", "La polea hace un chirrido al girar",
                 "Desgaste excesivo en los piñones", "El acople entre motor y bomba está flojo"],
    "fugas": ["Escape de lubricante debajo del equipo", "Charco de líquido junto al tanque",
              "Se sale el refrigerante por la junta", "Hay goteo constante en la tubería del aire comprimido"],
    "instrumentación": ["La lectura del termómetro digital no coincide con la real", "El caudalímetro muestra cero aunque hay flujo",
                        "Medidor de presión con aguja pegada", "La sonda de pH da mediciones que saltan"],
}
NEGACION = ["Hay fuga de aceite en la bomba 3", "No hay fuga de aceite en la bomba 3", "Escape de lubricante en la bomba 3"]

EQUIPOS = list(EJEMPLOS)
X_E = [t for c in EQUIPOS for t in EJEMPLOS[c]]
Y_E = [c for c in EQUIPOS for _ in EJEMPLOS[c]]
X_P = [t for c in EQUIPOS for t in PRUEBA[c]]
Y_P = [c for c in EQUIPOS for _ in PRUEBA[c]]


def por_centroide(v_e: np.ndarray, v_p: np.ndarray) -> list[str]:
    centros = np.stack([v_e[[i for i, y in enumerate(Y_E) if y == c]].mean(0) for c in EQUIPOS])
    centros /= np.linalg.norm(centros, axis=1, keepdims=True) + 1e-9
    v_p = v_p / (np.linalg.norm(v_p, axis=1, keepdims=True) + 1e-9)
    return [EQUIPOS[i] for i in (v_p @ centros.T).argmax(1)]


def main() -> None:
    palabras = lambda s: re.findall(r"\w+", s.lower())
    vocabulario = sorted({w for s in X_E + X_P for w in palabras(s)})
    bolsa = lambda textos: np.array([[Counter(palabras(s))[w] for w in vocabulario] for s in textos], float)
    pred = por_centroide(bolsa(X_E), bolsa(X_P))
    resultados = [{"representacion": "bolsa de palabras", "aciertos": sum(p == y for p, y in zip(pred, Y_P)),
                   "predicciones": pred}]
    for modelo, commit, prefijo in CODIFICADORES:
        st = SentenceTransformer(modelo, revision=commit, device="cpu", model_kwargs={"dtype": torch.float32})
        codificar = lambda textos: st.encode([prefijo + t for t in textos], normalize_embeddings=True)
        pred = por_centroide(codificar(X_E), codificar(X_P))
        n = codificar(NEGACION)
        resultados.append({"representacion": modelo, "aciertos": sum(p == y for p, y in zip(pred, Y_P)),
                           "predicciones": pred, "similitud_fuga_no_fuga": round(float(n[0] @ n[1]), 2),
                           "similitud_fuga_escape": round(float(n[0] @ n[2]), 2)})
    for r in resultados:
        extra = (f" | fuga/no fuga {r['similitud_fuga_no_fuga']:.2f}, fuga/escape {r['similitud_fuga_escape']:.2f}"
                 if "similitud_fuga_no_fuga" in r else "")
        print(f"{r['representacion'].split('/')[-1]:40} {r['aciertos']}/16{extra}")
    guardar_json("codificador_5b.json", {"ejemplos_por_equipo": 3, "prueba": len(X_P), "reales": Y_P,
                                         "textos_prueba": X_P, "negacion": NEGACION, "resultados": resultados})


if __name__ == "__main__":
    main()
