from bounded_contexts.auth.exceptions import BaseAuthException


class IncorrectLoginDataException(BaseAuthException):
    def __init__(self, email: str) -> None:
        self.email = email

    def __str__(self) -> str:
        return f"Exception(email={self.email})"
