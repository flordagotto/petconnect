from bounded_contexts.adoptions_domain.exceptions.base_animal_exception import (
    BaseAnimalException,
)


class ApplicationNotFoundByIdException(BaseAnimalException):
    def __init__(self, entity_id: str) -> None:
        self.entity_id = entity_id


class ApplicationNotFoundByAnimalIdException(BaseAnimalException):
    def __init__(self, animal_id: str) -> None:
        self.animal_id = animal_id
