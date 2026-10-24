(define (problem ot-523)
  (:domain mantenia)
  (:objects marta luis - tecnico
            compresor2 - equipo
            rodamientos - repuesto
            base bodega-sur planta-sur - lugar)
  (:init (en marta base) (en luis base)
         (ubicado compresor2 planta-sur) (encendido compresor2) (averiado compresor2)
         (almacenado rodamientos bodega-sur) (compatible rodamientos compresor2)
         (certificado marta compresor2))   ; la certificación de luis venció: no aparece
  (:goal (en-servicio compresor2)))
