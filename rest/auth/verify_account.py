from pydantic import BaseModel
from bounded_contexts.auth.use_cases import (
    VerifyAccountUseCase,
    ResendVerificationRequest,
)
from infrastructure.rest import BaseAPIController


class VerifyAccountController(BaseAPIController):
    class VerifyTokenBody(BaseModel):
        verification_token: str

    async def post(self, body: VerifyTokenBody) -> None:
        use_case: VerifyAccountUseCase = self.dependencies.resolve(VerifyAccountUseCase)

        await use_case.execute(
            VerifyAccountUseCase.Request(
                verification_token=body.verification_token,
            )
        )

    class ResendVerificationRequestBody(BaseModel):
        email: str

    async def post_resend(self, body: ResendVerificationRequestBody) -> None:
        use_case: ResendVerificationRequest = self.dependencies.resolve(
            ResendVerificationRequest
        )

        await use_case.execute(
            ResendVerificationRequest.Request(
                email=body.email,
            )
        )

    def register_routes(self) -> None:
        PREFIX: str = "/auth/verify_account"

        self._register_post_route(f"{PREFIX}", method=self.post)
        self._register_post_route(f"{PREFIX}/resend", method=self.post_resend)
