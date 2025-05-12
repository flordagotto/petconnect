from dataclasses import dataclass
from bounded_contexts.auth.use_cases import BaseAuthUseCase
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class RequestPasswordResetUseCase(BaseAuthUseCase):
    @dataclass
    class Request:
        email: str

    @unit_of_work
    async def execute(
        self,
        request: Request,
        uow: UnitOfWork,
    ) -> None:
        await self.accounts_service.request_password_reset(
            uow=uow,
            email=request.email,
        )
