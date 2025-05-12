from dataclasses import dataclass
from bounded_contexts.auth.use_cases import BaseAuthUseCase
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class ResetPasswordUseCase(BaseAuthUseCase):
    @dataclass
    class Request:
        reset_password_token: str
        new_password: str

    @unit_of_work
    async def execute(
        self,
        request: Request,
        uow: UnitOfWork,
    ) -> None:
        await self.accounts_service.reset_account_password(
            uow=uow,
            reset_password_token=request.reset_password_token,
            new_password=request.new_password,
        )
