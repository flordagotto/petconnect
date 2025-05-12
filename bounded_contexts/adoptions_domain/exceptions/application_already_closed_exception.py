from bounded_contexts.adoptions_domain.exceptions import BaseAnimalException


class AdoptionApplicationAlreadyClosedException(BaseAnimalException):
    def __init__(self, adoption_application_id: str) -> None:
        self.adoption_application_id = adoption_application_id
