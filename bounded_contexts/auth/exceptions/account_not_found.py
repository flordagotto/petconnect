from bounded_contexts.auth.exceptions import BaseAuthException


class AccountNotFoundException(BaseAuthException):
    pass


class AccountNotFoundByEmailException(BaseAuthException):
    def __init__(
        self,
        email: str,
    ) -> None:
        self.email = email

    def __str__(self) -> str:
        return f"Exception(email={self.email})"


class AccountNotFoundByIdException(BaseAuthException):
    def __init__(
        self,
        entity_id: str,
    ) -> None:
        self.entity_id = entity_id

    def __str__(self) -> str:
        return f"Exception(entity_id={self.entity_id})"
