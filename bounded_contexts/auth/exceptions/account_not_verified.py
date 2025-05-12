from bounded_contexts.auth.exceptions import BaseAuthException


class AccountNotVerifiedException(BaseAuthException):
    def __init__(self, account_id: str) -> None:
        self.account_id = account_id

    def __str__(self) -> str:
        return f"Exception(account_id={self.account_id})"


class AccountAlreadyVerifiedException(BaseAuthException):
    def __init__(self, account_id: str, email: str) -> None:
        self.account_id = account_id
        self.email = email

    def __str__(self) -> str:
        return f"Exception(account_id={self.account_id}, email={self.email})"
