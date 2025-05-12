from bounded_contexts.pets_domain.exceptions import BasePetsException


class PetSightNotFoundException(BasePetsException):
    # Not sure if we are going to need this
    def __init__(self, entity_id: str) -> None:
        self.entity_id = entity_id

    def __str__(self) -> str:
        return f"Exception(entity_id={self.entity_id})"
