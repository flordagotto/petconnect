from bounded_contexts.pets_domain.exceptions import BasePetsException


class SightForNotLostPetException(BasePetsException):
    def __init__(self, pet_id: str) -> None:
        self.pet_id = pet_id

    def __str__(self) -> str:
        return f"Exception(pet_id={self.pet_id})"
