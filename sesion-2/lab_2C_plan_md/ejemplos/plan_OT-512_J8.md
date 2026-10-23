# Plan: restablecer la bomba 3 (OT-512)

## Objetivo
Bomba 3 en servicio hoy antes de las ~~14:00~~ 16:00 (plazo aprobado a las
10:40), con el sello cambiado y la prueba de presión aprobada.

## Contexto
- OT-512 (sistema de mantenimiento): fuga en el sello de la bomba 3,
  Planta Norte. Sello SM-40 en la bodega (1 unidad).
- Ana está certificada para la bomba 3; Luis no.
- Supuesto: la línea 2 opera sin la bomba 3.

## Alcance
- Incluye: cambio del sello, prueba y arranque.
- Fuera de alcance: el motor, la línea 2 y las compras.

## Restricciones
- Bloqueo y etiquetado obligatorio; solo personal certificado.

## Pasos
- [x] 1. Retirar el sello SM-40 de la bodega
        → sello en mano · Verif.: salida en inventario
- [x] 2. Bloquear y etiquetar la bomba 3
        → sin energía · Verif.: candado de Ana puesto
- [x] 3. Cambiar el sello (requiere 1 y 2)
        → sello nuevo · Verif.: lista del fabricante
- [ ] 3b. Traer un sello SM-40 de la Planta Sur (nuevo)
        → sello en mano · Verif.: remisión de la Planta Sur
- [ ] 3c. Repetir el cambio de sello (requiere 3b; nuevo)
        → sello nuevo · Verif.: lista del fabricante
- [ ] 4. Prueba de presión (requiere 3c; el primer intento falló)
        → sin fuga · Verif.: 30 min a presión nominal
- [ ] 5. APROBACIÓN: el supervisor autoriza arrancar (requiere 4)
        → autorización · Verif.: firma en la OT-512
- [ ] 6. Retirar el bloqueo y arrancar (requiere 5)
        → en servicio · Verif.: caudal nominal

## Criterios de aceptación
- En servicio antes del plazo, sin fuga tras 30 min y con la OT-512
  cerrada en el sistema de mantenimiento.

## Riesgos y aprobaciones
| Riesgo | Señal | Respuesta |
|---|---|---|
| Sello defectuoso | Fuga en la prueba | Pedir un sello a la Planta Sur |
| Ana no disponible | Aviso de ausencia | Escalar al jefe; no reasignar a Luis |

## Registro de avance
- 09:10 · Paso 1 cumplido (salida en inventario).
- 09:45 · Paso 2 cumplido (candado de Ana puesto).
- 10:20 · Paso 3 cumplido (lista del fabricante).
- 10:30 · Paso 4 falló: fuga; el sello vino defectuoso.
- 10:35 · Replanificación: pasos 3b y 3c; el plazo pasa a las 16:00.
- 10:40 · El supervisor aprueba el nuevo plazo.
