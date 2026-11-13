# Laboratorio 7A: origen de los modelos y de las herramientas

## La red de la alarma

La red es de Judea Pearl: Pearl, J. (1988). *Probabilistic Reasoning in Intelligent Systems*. Morgan Kaufmann. Las tablas son las de Russell, S. y Norvig, P. (2021). *Artificial Intelligence: A Modern Approach*, 4.ª ed., cap. 13, fig. 13.2. Pearson. El módulo `redes.py` arma la red desde esas tablas:
- P(robo) = 0.001 y P(sismo) = 0.002;
- P(alarma) = 0.95, 0.94, 0.29 y 0.001, según el robo y el sismo;
- P(llama Juan) = 0.90 y 0.05, y P(llama María) = 0.70 y 0.01, según la alarma.

La red llamada «alarm» que trae pyAgrum es otra: la red médica ALARM, de 37 nodos. Este laboratorio no la usa.

## El petrolero

El problema es de Raiffa, H. (1968). *Decision Analysis*. Addison-Wesley. Los números son los que reproduce Shenoy, P. P. (1995). Representing and solving asymmetric decision problems using valuation networks. *Fifth International Workshop on AI and Statistics*. El pozo está seco, húmedo o empapado con 0.5, 0.3 y 0.2. Perforar paga -70, 50 o 200. La prueba sísmica cuesta 10.

pyAgrum trae el mismo ejemplo en su documentación (`OilWildcatter.bgum`). Allí los resultados de la prueba se llaman «diffuse», «open» y «closed». Este laboratorio arma el diagrama desde los números, con los nombres «sin estructura», «abierta» y «cerrada».

## La alarma de vibración y la bomba de MantenIA

MantenIA es una empresa ficticia del curso. Sus cifras son ilustrativas. En la alarma de vibración, fallan el 2 % de las bombas y la alarma acierta el 95 %. Reemplazar la bomba cuesta 8 millones de pesos, y una falla sin aviso, 40.

## pyAgrum

pyAgrum 3.3.2, de Pierre-Henri Wuillemin y Christophe Gonzales, según sus metadatos en PyPI. Doble licencia: LGPLv3 o MIT. <https://agrum.gitlab.io/> · <https://pypi.org/project/pyagrum/3.3.2/>
