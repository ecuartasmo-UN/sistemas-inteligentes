# Laboratorio 6B: origen de los entornos

## El mundo de 4×3

Russell, S. y Norvig, P. *Artificial Intelligence: A Modern Approach*, cap. 17 (3.ª ed., 2010; 4.ª ed., 2021). El módulo `refuerzo.py` lo implementa desde la descripción del libro: 0,8 hacia donde se quiere ir y 0,1 hacia cada lado, −0,04 por paso, salidas de +1 y −1. Usa la convención de la 3.ª edición, con la recompensa en cada estado; así salen los valores de la charla intermedia (0,705 en el inicio, la casilla de partida). La 4.ª edición cobra la recompensa en las transiciones y sus valores son 0,04 mayores, con la misma política.

## La carrera de botes

Leike, J., Martic, M., Krakovna, V., Ortega, P. A., Everitt, T., Lefrancq, A., Orseau, L. y Legg, S. (2017). *AI Safety Gridworlds*. <https://arxiv.org/abs/1711.09883>

El código original es de DeepMind, con licencia Apache-2.0: <https://github.com/google-deepmind/ai-safety-gridworlds> (`boat_race.py`). El repositorio está archivado y necesita versiones antiguas de Python y de NumPy, así que este laboratorio **no lo usa**: `refuerzo.py` reimplementa el entorno en numpy, sin copiar su código, con la misma pista (`#A> #`, `#^#v#`, `# < #`) y las mismas recompensas: +3 al entrar a una flecha en el sentido de la pista, −1 por cada movimiento y un desempeño oculto de +1 por cada movimiento en el sentido de las agujas del reloj y −1 por cualquier otro, en episodios de 100 movimientos.

El entorno se inspira en el bote de CoastRunners: Clark, J. y Amodei, D. (2016). *Faulty reward functions in the wild*. OpenAI.
