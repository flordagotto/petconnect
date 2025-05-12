from bounded_contexts.pets_domain.exceptions import BasePetsException


class PetNotFoundException(BasePetsException):
    # Not sure if we are going to need this
    def __init__(self, animal_name: str, profile_id: str) -> None:
        self.animal_name = animal_name
        self.profile_id = profile_id

    def __str__(self) -> str:
        return f"Exception(name={self.animal_name},profile_id={self.profile_id})"


class PetNotFoundByIdException(BasePetsException):
    def __init__(self, entity_id: str) -> None:
        self.entity_id = entity_id


class PetNotFoundByAdoptionAnimalIdException(BasePetsException):
    def __init__(self, adoption_animal_id: str) -> None:
        self.adoption_animal_id = adoption_animal_id
