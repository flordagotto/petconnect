from dataclasses import dataclass
from bounded_contexts.auth.enum import TokenTypes
from bounded_contexts.auth.exceptions import InvalidTokenDataException


@dataclass
class TokenData:
    account_id: str
    token_type: TokenTypes

    @staticmethod
    def to_dict(token_data: "TokenData") -> dict[str, str]:
        return {
            "account_id": token_data.account_id,
            "token_type": token_data.token_type.value,
        }

    @staticmethod
    def from_dict(token_data_dict: dict) -> "TokenData":
        account_id: str | None = token_data_dict.get("account_id", None)
        token_type: str | None = token_data_dict.get("token_type", None)

        if (
            token_type not in list(map(lambda t_type: t_type.value, TokenTypes))
            or not account_id
        ):
            raise InvalidTokenDataException(token_data_dict)

        return TokenData(
            account_id=token_data_dict["account_id"],
            token_type=TokenTypes(token_data_dict["token_type"]),
        )
