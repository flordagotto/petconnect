from dataclasses import dataclass
from bounded_contexts.auth.use_cases import BaseAuthUseCase
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class VerifyAccountUseCase(BaseAuthUseCase):
    @dataclass
    class Request:
        verification_token: str

    @unit_of_work
    async def execute(
        self,
        request: Request,
        uow: UnitOfWork,
    ) -> None:
        await self.accounts_service.verify_account(
            uow=uow,
            verification_token=request.verification_token,
        )
