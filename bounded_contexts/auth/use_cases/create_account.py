from dataclasses import dataclass
from bounded_contexts.auth.entities import Account
from bounded_contexts.auth.use_cases import BaseAuthUseCase
from bounded_contexts.auth.views import AccountView
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class CreateAccountUseCase(BaseAuthUseCase):
    @dataclass
    class Request:
        email: str
        password: str

    @unit_of_work
    async def execute(
        self,
        request: Request,
        uow: UnitOfWork,
    ) -> AccountView:
        account: Account = await self.accounts_service.create_account(
            uow=uow,
            email=request.email,
            password=request.password,
        )

        return self.account_view_factory.create_account_view(
            account=account,
        )
