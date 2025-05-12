from bounded_contexts.auth.enum import TokenTypes
from bounded_contexts.auth.exceptions import BaseAuthException


class InvalidTokenDataException(BaseAuthException):
    def __init__(self, token: str | dict) -> None:
        self.token = token

    def __str__(self) -> str:
        return f"Exception(token={self.token})"


class GenerateTokenException(BaseAuthException):
    def __init__(self, payload: dict) -> None:
        self.payload = payload


class DecodeTokenException(BaseAuthException):
    def __init__(self, token: str) -> None:
        self.token = token


class UnexpectedTokenException(BaseAuthException):
    def __init__(
        self, expected_token_type: TokenTypes, actual_token_type: TokenTypes
    ) -> None:
        self.expected_token_type = expected_token_type
        self.actual_token_type = actual_token_type
