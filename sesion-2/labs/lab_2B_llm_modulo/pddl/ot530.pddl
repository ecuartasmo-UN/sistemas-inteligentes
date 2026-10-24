(define (problem ot-530)
  (:domain mantenia)
  (:objects ana luis marta - tecnico
            bomba3 compresor2 caldera1 - equipo
            sello rodamiento quemador - repuesto
            base bodega planta-norte planta-sur - lugar)
  (:init (en ana base) (en luis base) (en marta planta-sur)
         (ubicado bomba3 planta-norte) (ubicado compresor2 planta-sur) (ubicado caldera1 planta-sur)
         (encendido bomba3) (encendido compresor2) (encendido caldera1)
         (averiado bomba3) (averiado compresor2) (averiado caldera1)
         (almacenado sello bodega) (almacenado rodamiento bodega) (almacenado quemador bodega)
         (compatible sello bomba3) (compatible rodamiento compresor2) (compatible quemador caldera1)
         (certificado ana bomba3) (certificado luis compresor2)
         (certificado marta compresor2) (certificado marta caldera1))
  (:goal (and (en-servicio bomba3) (en-servicio compresor2) (en-servicio caldera1))))
