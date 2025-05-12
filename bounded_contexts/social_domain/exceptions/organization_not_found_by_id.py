from bounded_contexts.social_domain.exceptions import BaseSocialException


class OrganizationNotFoundByIdException(BaseSocialException):
    def __init__(self, entity_id: str) -> None:
        self.entity_id = entity_id

    def __str__(self) -> str:
        return f"Exception(entity_id={self.entity_id})"
