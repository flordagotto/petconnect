from fastapi import HTTPException
from bounded_contexts.auth.exceptions import (
    EmailAlreadyRegisteredException,
    IncorrectLoginDataException,
    AccountNotFoundException,
    AccountNotFoundByEmailException,
    AccountNotFoundByIdException,
    AccountNotVerifiedException,
    InvalidTokenDataException,
    DecodeTokenException,
    GenerateTokenException,
    UnexpectedTokenException,
    AccountAlreadyVerifiedException,
)
from rest.error_manager import BaseErrorManager, ErrorContainer
from rest.error_messages import MessagesConfig


class AuthErrorManager(BaseErrorManager):
    def __init__(self, messages_config: MessagesConfig) -> None:
        self.messages_config = messages_config

    def create_error_dictionary(self) -> ErrorContainer:
        return {
            EmailAlreadyRegisteredException: HTTPException(
                status_code=409,
                detail=self.messages_config.auth_messages.email_already_registered,
            ),
            IncorrectLoginDataException: HTTPException(
                status_code=401,
                detail=self.messages_config.auth_messages.incorrect_login_data,
            ),
            AccountNotFoundException: HTTPException(
                status_code=404,
                detail=self.messages_config.auth_messages.account_not_found,
            ),
            AccountNotFoundByEmailException: HTTPException(
                status_code=404,
                detail=self.messages_config.auth_messages.account_not_found_by_email,
            ),
            AccountNotFoundByIdException: HTTPException(
                status_code=404,
                detail=self.messages_config.auth_messages.account_not_found_by_id,
            ),
            AccountNotVerifiedException: HTTPException(
                status_code=400,
                detail=self.messages_config.auth_messages.account_not_verified,
            ),
            InvalidTokenDataException: HTTPException(
                status_code=400,
                detail=self.messages_config.auth_messages.invalid_data_token,
            ),
            DecodeTokenException: HTTPException(
                status_code=400,
                detail=self.messages_config.auth_messages.decode_token,
            ),
            GenerateTokenException: HTTPException(
                status_code=500,
                detail=self.messages_config.auth_messages.not_generated_token,
            ),
            UnexpectedTokenException: HTTPException(
                status_code=400,
                detail=self.messages_config.auth_messages.unexpected_token,
            ),
            AccountAlreadyVerifiedException: HTTPException(
                status_code=400,
                detail=self.messages_config.auth_messages.account_already_verified_exception,
            ),
        }
