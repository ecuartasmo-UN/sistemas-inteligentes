"""Árboles de decisión, reglas, ensambles y costo del error (charla inicial; prepara el Laboratorio 6A).

Cuatro ejemplos clásicos:
- el clima de Quinlan (1986), tabla 1: la entropía y la ganancia de información de cada pregunta, y el árbol de ID3;
- el Titanic (titanic3, Vanderbilt): un árbol de profundidad 3 y sus reglas, la regla «mujeres y niños primero»,
  el sobreajuste según la profundidad, la validación cruzada y dos ensambles;
- el German Credit (UCI, Statlog): el costo total según el umbral de decisión, con la matriz de costos 5 a 1;
- Mushroom (UCI): la regla del olor.

Uso, desde esta carpeta:  python arboles_6a.py
Requiere scikit-learn y pandas. La primera vez descarga los tres conjuntos (unos 300 KB) en datos/.
Escribe los números en salidas/arboles_6a.json.
"""
import io
import time
import zipfile
from math import log2

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_predict, cross_val_score
from sklearn.tree import DecisionTreeClassifier

from comun import DATOS, descargar, guardar_json

SEMILLA = 7
URL_TITANIC = "https://hbiostat.org/data/repo/titanic3.csv"
URL_CREDITO = "https://archive.ics.uci.edu/static/public/144/statlog+german+credit+data.zip"
URL_HONGOS = "https://archive.ics.uci.edu/static/public/73/mushroom.zip"

# Quinlan (1986), tabla 1: pronóstico, temperatura, humedad, viento y clase (P = jugar, N = no jugar)
CLIMA = [("soleado", "caliente", "alta", "no", "N"), ("soleado", "caliente", "alta", "sí", "N"),
         ("nublado", "caliente", "alta", "no", "P"), ("lluvioso", "templado", "alta", "no", "P"),
         ("lluvioso", "fresco", "normal", "no", "P"), ("lluvioso", "fresco", "normal", "sí", "N"),
         ("nublado", "fresco", "normal", "sí", "P"), ("soleado", "templado", "alta", "no", "N"),
         ("soleado", "fresco", "normal", "no", "P"), ("lluvioso", "templado", "normal", "no", "P"),
         ("soleado", "templado", "normal", "sí", "P"), ("nublado", "templado", "alta", "sí", "P"),
         ("nublado", "caliente", "normal", "no", "P"), ("lluvioso", "templado", "alta", "sí", "N")]
ATRIBUTOS = ["pronóstico", "temperatura", "humedad", "viento"]


def entropia(clases) -> float:
    n = len(clases)
    return -sum(clases.count(c) / n * log2(clases.count(c) / n) for c in set(clases)) if n else 0.0


def ganancias(filas) -> dict:
    base = entropia([f[4] for f in filas])
    salida = {}
    for j, nombre in enumerate(ATRIBUTOS):
        resto = sum(len(g) / len(filas) * entropia([f[4] for f in g])
                    for g in ([f for f in filas if f[j] == v] for v in sorted({f[j] for f in filas})))
        salida[nombre] = round(base - resto, 3)
    return salida


def quinlan() -> dict:
    raiz = ganancias(CLIMA)
    ramas = {}
    for valor in ("soleado", "nublado", "lluvioso"):
        sub = [f for f in CLIMA if f[0] == valor]
        ramas[valor] = {"casos": len(sub), "P": sum(f[4] == "P" for f in sub), "N": sum(f[4] == "N" for f in sub),
                        "entropia": round(entropia([f[4] for f in sub]), 3),
                        "ganancias": {k: v for k, v in ganancias(sub).items() if k != "pronóstico"}}
    return {"tabla": CLIMA, "entropia_raiz": round(entropia([f[4] for f in CLIMA]), 3), "ganancias_raiz": raiz,
            "ramas": ramas}


def titanic() -> dict:
    t = pd.read_csv(descargar(URL_TITANIC, "titanic3.csv"))
    # Sin nombre, boleto, cabina, bote ni cuerpo: no son rasgos del pasajero o revelan la respuesta (fuga de información)
    x = pd.DataFrame({"clase": t.pclass, "mujer": (t.sex == "female").astype(int), "edad": t.age,
                      "hermanos_o_conyuge": t.sibsp, "padres_o_hijos": t.parch, "tarifa": t.fare,
                      "embarco_en_C": (t.embarked == "C").astype(int), "embarco_en_Q": (t.embarked == "Q").astype(int)})
    y = t.survived.to_numpy()
    cv = StratifiedKFold(5, shuffle=True, random_state=SEMILLA)
    profundidades = []
    for d in (1, 2, 3, 4, 5, 6, 8, 10, 12, None):
        arbol = DecisionTreeClassifier(max_depth=d, random_state=SEMILLA)
        a = cross_val_score(arbol, x, y, cv=cv)
        arbol.fit(x, y)
        profundidades.append({"profundidad": d if d else "sin límite", "validacion_cruzada": round(a.mean(), 3),
                              "desviacion": round(a.std(), 3), "entrenamiento": round(arbol.score(x, y), 3),
                              "hojas": int(arbol.get_n_leaves())})
    ensambles = {}
    for nombre, modelo in (("bosque aleatorio", RandomForestClassifier(300, min_samples_leaf=3, random_state=SEMILLA)),
                           ("boosting por gradiente", HistGradientBoostingClassifier(random_state=SEMILLA))):
        inicio = time.perf_counter()
        a = cross_val_score(modelo, x, y, cv=cv)
        ensambles[nombre] = {"validacion_cruzada": round(a.mean(), 3), "desviacion": round(a.std(), 3),
                             "segundos": round(time.perf_counter() - inicio, 1)}
    arbol3 = DecisionTreeClassifier(max_depth=3, random_state=SEMILLA).fit(x, y)
    arbol_cv = cross_val_score(DecisionTreeClassifier(max_depth=3, random_state=SEMILLA), x, y, cv=cv)
    pliegues = [round(v, 3) for v in arbol_cv]
    regla = ((x.mujer == 1) | (x.edad < 14)).astype(int).to_numpy()   # «mujeres y niños primero»
    return {"pasajeros": len(t), "sobrevivientes": int(y.sum()), "proporcion": round(y.mean(), 3),
            "linea_base": round(1 - y.mean(), 3), "regla_experto": round((regla == y).mean(), 3),
            "solo_mujeres": round(((x.mujer == 1).astype(int).to_numpy() == y).mean(), 3),
            "profundidades": profundidades, "ensambles": ensambles, "pliegues_arbol3": pliegues,
            "arbol3": nodos(arbol3, list(x.columns))}


def nodos(arbol, nombres) -> list:
    """El árbol como lista de nodos: pregunta, umbral, hijos y, en las hojas, los casos de cada clase."""
    t = arbol.tree_
    salida = []
    for i in range(t.node_count):
        casos = [int(round(v)) for v in t.value[i][0] * t.n_node_samples[i]]
        salida.append({"id": i, "atributo": nombres[t.feature[i]] if t.children_left[i] != -1 else None,
                       "umbral": round(float(t.threshold[i]), 2) if t.children_left[i] != -1 else None,
                       "si": int(t.children_left[i]), "no": int(t.children_right[i]),
                       "no_sobreviven": casos[0], "sobreviven": casos[1]})
    return salida


def credito() -> dict:
    with zipfile.ZipFile(descargar(URL_CREDITO, "german_credit.zip")) as z:
        g = pd.read_csv(io.BytesIO(z.read("german.data")), sep=" ", header=None)
    y = (g[20] == 2).astype(int).to_numpy()        # 1 = mal pagador
    x = pd.get_dummies(g.drop(columns=[20]), dtype=float)
    x.columns = x.columns.astype(str)
    cv = StratifiedKFold(5, shuffle=True, random_state=SEMILLA)
    p = cross_val_predict(RandomForestClassifier(300, min_samples_leaf=3, random_state=SEMILLA), x, y, cv=cv,
                          method="predict_proba")[:, 1]
    curva = []
    for u in np.round(np.arange(0.05, 0.96, 0.01), 2):
        pred = (p >= u).astype(int)
        fn = int(((pred == 0) & (y == 1)).sum())        # mal pagador aprobado: cuesta 5
        fp = int(((pred == 1) & (y == 0)).sum())        # buen pagador rechazado: cuesta 1
        curva.append({"umbral": float(u), "costo": 5 * fn + fp, "exactitud": round(float((pred == y).mean()), 3),
                      "malos_aprobados": fn, "buenos_rechazados": fp})
    def punto(u):
        pred = (p >= u).astype(int)
        fn, fp = int(((pred == 0) & (y == 1)).sum()), int(((pred == 1) & (y == 0)).sum())
        return {"umbral": round(u, 3), "costo": 5 * fn + fp, "exactitud": round(float((pred == y).mean()), 3),
                "malos_aprobados": fn, "buenos_rechazados": fp,
                "malos_rechazados": int(((pred == 1) & (y == 1)).sum()), "buenos_aprobados": int(((pred == 0) & (y == 0)).sum())}
    return {"clientes": len(g), "malos": int(y.sum()), "aprobar_a_todos": 5 * int(y.sum()),
            "rechazar_a_todos": int((1 - y).sum()), "umbral_0_5": punto(0.5), "umbral_costo": punto(1 / 6),
            "curva": curva}


def hongos() -> dict:
    with zipfile.ZipFile(descargar(URL_HONGOS, "mushroom.zip")) as z:
        m = pd.read_csv(io.BytesIO(z.read("agaricus-lepiota.data")), header=None)
    venenoso = (m[0] == "p").to_numpy()
    sin_peligro = m[5].isin(["n", "a", "l"]).to_numpy()     # sin olor, almendra o anís
    return {"hongos": len(m), "venenosos": int(venenoso.sum()),
            "acierto_regla_olor": round(float((sin_peligro == ~venenoso).mean()), 4),
            "venenosos_sin_olor": int((venenoso & (m[5] == "n").to_numpy()).sum())}


def main() -> None:
    DATOS.mkdir(exist_ok=True)
    resultado = {"quinlan": quinlan(), "titanic": titanic(), "credito": credito(), "hongos": hongos()}
    q, t, c, h = resultado["quinlan"], resultado["titanic"], resultado["credito"], resultado["hongos"]
    print("Quinlan: entropía", q["entropia_raiz"], "ganancias", q["ganancias_raiz"])
    print(f"Titanic: {t['pasajeros']} pasajeros, {t['proporcion']:.1%} sobrevive; regla de experto {t['regla_experto']:.1%}")
    for p in t["profundidades"]:
        print(f"  profundidad {p['profundidad']}: validación cruzada {p['validacion_cruzada']:.3f}, entrenamiento {p['entrenamiento']:.3f}")
    print("  ensambles:", t["ensambles"])
    print(f"German Credit: umbral 0,5 → costo {c['umbral_0_5']['costo']} (exactitud {c['umbral_0_5']['exactitud']}); "
          f"umbral 1/6 → costo {c['umbral_costo']['costo']} (exactitud {c['umbral_costo']['exactitud']}); "
          f"rechazar a todos {c['rechazar_a_todos']}, aprobar a todos {c['aprobar_a_todos']}")
    print(f"Mushroom: la regla del olor acierta {h['acierto_regla_olor']:.2%}")
    guardar_json("arboles_6a.json", resultado)


if __name__ == "__main__":
    main()
