from bounded_contexts.pets_domain.exceptions import BasePetsException


class PetUnauthorizedAccessException(BasePetsException):
    def __init__(self, actor_account_id: str, pet_id: str) -> None:
        self.actor_account_id = actor_account_id
        self.pet_id = pet_id
