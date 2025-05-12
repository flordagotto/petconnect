from bounded_contexts.pets_domain.exceptions import BasePetsException


class OwnerIsNotAPersonalProfileException(BasePetsException):
    def __init__(self, profile_id: str) -> None:
        self.profile_id = profile_id

    def __str__(self) -> str:
        return f"Exception(profile_id={self.profile_id})"
