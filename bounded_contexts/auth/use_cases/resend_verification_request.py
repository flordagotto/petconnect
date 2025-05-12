from dataclasses import dataclass
from bounded_contexts.auth.use_cases import BaseAuthUseCase
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class ResendVerificationRequest(BaseAuthUseCase):
    @dataclass
    class Request:
        email: str

    @unit_of_work
    async def execute(
        self,
        request: Request,
        uow: UnitOfWork,
    ) -> None:
        # Ideally, there should be limits to the amount of requests. Not a priority now.

        await self.accounts_service.resend_verification_request(
            uow=uow,
            email=request.email,
        )
