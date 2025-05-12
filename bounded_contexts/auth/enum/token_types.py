from enum import Enum


class TokenTypes(Enum):
    ACCESS_TOKEN: str = "access_token"
    VERIFY_ACCOUNT_TOKEN: str = "verify_account_token"
    RESET_PASSWORD_TOKEN: str = "reset_password_token"
