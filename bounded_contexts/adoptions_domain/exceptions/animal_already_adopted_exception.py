from bounded_contexts.adoptions_domain.exceptions import BaseAnimalException


class AnimalAlreadyAdoptedException(BaseAnimalException):
    def __init__(self, animal_id: str) -> None:
        self.animal_id = animal_id
