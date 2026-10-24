(define (problem ot-518)
  (:domain mantenia)
  (:objects ana luis - tecnico
            bomba3 compresor2 - equipo
            sello rodamiento - repuesto
            base bodega planta-norte planta-sur - lugar)
  (:init (en ana base) (en luis base)
         (ubicado bomba3 planta-norte) (ubicado compresor2 planta-sur)
         (encendido bomba3) (encendido compresor2)
         (averiado bomba3) (averiado compresor2)
         (almacenado sello bodega) (almacenado rodamiento bodega)
         (compatible sello bomba3) (compatible rodamiento compresor2)
         (certificado ana bomba3) (certificado luis compresor2))
  (:goal (and (en-servicio bomba3) (en-servicio compresor2))))
