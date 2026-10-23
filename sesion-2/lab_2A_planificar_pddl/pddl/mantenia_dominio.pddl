(define (domain mantenia)
  (:requirements :strips :typing)
  (:types tecnico equipo repuesto lugar)
  (:predicates
    (en ?t - tecnico ?l - lugar)
    (ubicado ?e - equipo ?l - lugar)
    (almacenado ?r - repuesto ?l - lugar)
    (lleva ?t - tecnico ?r - repuesto)
    (compatible ?r - repuesto ?e - equipo)
    (certificado ?t - tecnico ?e - equipo)
    (encendido ?e - equipo)
    (bloqueado ?e - equipo)
    (averiado ?e - equipo)
    (reparado ?e - equipo)
    (en-servicio ?e - equipo))

  (:action desplazarse
    :parameters (?t - tecnico ?desde - lugar ?hacia - lugar)
    :precondition (en ?t ?desde)
    :effect (and (en ?t ?hacia) (not (en ?t ?desde))))

  (:action retirar-repuesto
    :parameters (?t - tecnico ?r - repuesto ?l - lugar)
    :precondition (and (en ?t ?l) (almacenado ?r ?l))
    :effect (and (lleva ?t ?r) (not (almacenado ?r ?l))))

  (:action bloquear
    :parameters (?t - tecnico ?e - equipo ?l - lugar)
    :precondition (and (en ?t ?l) (ubicado ?e ?l) (encendido ?e)
                       (certificado ?t ?e))
    :effect (and (bloqueado ?e) (not (encendido ?e))))

  (:action reparar
    :parameters (?t - tecnico ?e - equipo ?r - repuesto ?l - lugar)
    :precondition (and (en ?t ?l) (ubicado ?e ?l) (bloqueado ?e)
                       (averiado ?e) (lleva ?t ?r) (compatible ?r ?e)
                       (certificado ?t ?e))
    :effect (and (reparado ?e) (not (averiado ?e)) (not (lleva ?t ?r))))

  (:action liberar
    :parameters (?t - tecnico ?e - equipo ?l - lugar)
    :precondition (and (en ?t ?l) (ubicado ?e ?l) (bloqueado ?e) (reparado ?e))
    :effect (and (en-servicio ?e) (encendido ?e) (not (bloqueado ?e))))
)
