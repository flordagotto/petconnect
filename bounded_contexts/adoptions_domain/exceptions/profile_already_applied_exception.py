from bounded_contexts.adoptions_domain.exceptions import BaseAnimalException


class ProfileAlreadyAppliedException(BaseAnimalException):
    def __init__(self, actor_account_id: str, animal_id: str) -> None:
        self.actor_account_id = actor_account_id
        self.animal_id = animal_id
