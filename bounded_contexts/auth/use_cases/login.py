from dataclasses import dataclass
from bounded_contexts.auth.entities import Account
from bounded_contexts.auth.use_cases import BaseAuthUseCase
from bounded_contexts.auth.views import TokenView
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class LoginUseCase(BaseAuthUseCase):
    @dataclass
    class Request:
        email: str
        password: str

    @unit_of_work
    async def execute(
        self,
        request: Request,
        uow: UnitOfWork,
    ) -> TokenView:
        account: Account = await self.accounts_service.get_account_by_email(
            uow=uow,
            email=request.email,
        )

        access_token: str = await self.accounts_service.get_login_token(
            account=account,
            password=request.password,
        )

        return self.account_view_factory.create_token_view(
            access_token=access_token,
        )
