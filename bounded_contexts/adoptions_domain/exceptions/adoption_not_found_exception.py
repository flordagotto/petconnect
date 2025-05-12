from bounded_contexts.adoptions_domain.exceptions.base_animal_exception import (
    BaseAnimalException,
)


class AdoptionNotFoundByIdException(BaseAnimalException):
    def __init__(self, entity_id: str) -> None:
        self.entity_id = entity_id


class AdoptionNotFoundByApplicationIdException(BaseAnimalException):
    def __init__(self, adoption_application_id: str) -> None:
        self.adoption_application_id = adoption_application_id
