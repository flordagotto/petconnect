from pydantic import BaseModel
from bounded_contexts.auth.entities import Account


class AccountView(BaseModel):
    entity_id: str
    email: str
    verified: bool


class TokenView(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AccountViewFactory:
    @staticmethod
    def create_account_view(account: Account) -> AccountView:
        return AccountView(
            entity_id=account.entity_id,
            email=account.email,
            verified=account.verified,
        )

    def create_token_view(self, access_token: str) -> TokenView:
        return TokenView(
            access_token=access_token,
        )
