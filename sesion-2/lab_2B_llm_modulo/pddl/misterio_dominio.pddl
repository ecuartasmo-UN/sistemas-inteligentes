(define (domain dominio-x)
  (:requirements :strips :typing)
  (:types brin talo quira suno)
  (:predicates
    (vosca ?x - brin ?w - suno)
    (melfa ?y - talo ?w - suno)
    (drupo ?z - quira ?w - suno)
    (tarsa ?x - brin ?z - quira)
    (plimo ?z - quira ?y - talo)
    (gavo ?x - brin ?y - talo)
    (lunte ?y - talo)
    (cresa ?y - talo)
    (fumpa ?y - talo)
    (nolda ?y - talo)
    (birta ?y - talo))

  (:action trolvar
    :parameters (?x - brin ?a - suno ?b - suno)
    :precondition (vosca ?x ?a)
    :effect (and (vosca ?x ?b) (not (vosca ?x ?a))))

  (:action pemsar
    :parameters (?x - brin ?z - quira ?w - suno)
    :precondition (and (vosca ?x ?w) (drupo ?z ?w))
    :effect (and (tarsa ?x ?z) (not (drupo ?z ?w))))

  (:action lorbar
    :parameters (?x - brin ?y - talo ?w - suno)
    :precondition (and (vosca ?x ?w) (melfa ?y ?w) (lunte ?y)
                       (gavo ?x ?y))
    :effect (and (cresa ?y) (not (lunte ?y))))

  (:action quindar
    :parameters (?x - brin ?y - talo ?z - quira ?w - suno)
    :precondition (and (vosca ?x ?w) (melfa ?y ?w) (cresa ?y)
                       (fumpa ?y) (tarsa ?x ?z) (plimo ?z ?y)
                       (gavo ?x ?y))
    :effect (and (nolda ?y) (not (fumpa ?y)) (not (tarsa ?x ?z))))

  (:action fasbar
    :parameters (?x - brin ?y - talo ?w - suno)
    :precondition (and (vosca ?x ?w) (melfa ?y ?w) (cresa ?y) (nolda ?y))
    :effect (and (birta ?y) (lunte ?y) (not (cresa ?y))))
)
