(define (problem ot-512-sin-solucion)
  (:domain mantenia)
  (:objects ana luis - tecnico
            bomba3 - equipo
            sello - repuesto
            base bodega planta-norte - lugar)
  (:init (en ana base) (en luis base)
         (ubicado bomba3 planta-norte) (encendido bomba3) (averiado bomba3)
         (almacenado sello bodega) (compatible sello bomba3)
         )
  (:goal (en-servicio bomba3)))
