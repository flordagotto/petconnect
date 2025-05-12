from bounded_contexts.adoptions_domain.exceptions import BaseAnimalException


class ApplicationByOrganizationNotValidException(BaseAnimalException):
    def __init__(self, actor_account_id: str) -> None:
        self.actor_account_id = actor_account_id
