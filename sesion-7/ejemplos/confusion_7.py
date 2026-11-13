"""Más mantenimiento, más fallas: una variable de confusión en MantenIA (charla de cierre).

Ejemplo ilustrativo, con cifras inventadas. MantenIA es una empresa ficticia.
- Las bombas viejas reciben más mantenimiento y también fallan más.
- En el total, el mantenimiento frecuente parece empeorar las cosas.
- Dentro de cada grupo de edad, el mantenimiento frecuente reduce las fallas.
La edad es la variable de confusión: causa las dos cosas.

Uso, desde esta carpeta:  python confusion_7.py
Solo usa la biblioteca estándar. Escribe salidas/confusion_7.json.
"""
from comun import guardar_json, red

# Bombas y fallas por edad y por mantenimiento (frecuente o poco)
TABLA = {
    "nuevas": {"frecuente": {"bombas": 60, "fallas": 3}, "poco": {"bombas": 240, "fallas": 24}},
    "viejas": {"frecuente": {"bombas": 240, "fallas": 72}, "poco": {"bombas": 60, "fallas": 27}},
}


def main() -> None:
    tasas = {}
    for edad, grupos in TABLA.items():
        tasas[edad] = {m: red(g["fallas"] / g["bombas"], 3) for m, g in grupos.items()}
    total = {}
    for m in ("frecuente", "poco"):
        bombas = sum(TABLA[e][m]["bombas"] for e in TABLA)
        fallas = sum(TABLA[e][m]["fallas"] for e in TABLA)
        total[m] = {"bombas": bombas, "fallas": fallas, "tasa": red(fallas / bombas, 3)}
    print(f"Total: frecuente {total['frecuente']['tasa']:.0%}, poco {total['poco']['tasa']:.0%}")
    for edad, t in tasas.items():
        print(f"{edad:7}: frecuente {t['frecuente']:.0%}, poco {t['poco']:.0%}")
    guardar_json("confusion_7.json", {"tabla": TABLA, "tasas_por_edad": tasas, "total": total})


if __name__ == "__main__":
    main()
