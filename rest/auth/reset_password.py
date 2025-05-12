from pydantic import BaseModel
from bounded_contexts.auth.use_cases import RequestPasswordResetUseCase
from bounded_contexts.auth.use_cases.reset_password import ResetPasswordUseCase
from infrastructure.rest import BaseAPIController


class ResetPasswordController(BaseAPIController):
    class RequestResetBody(BaseModel):
        email: str

    async def post_request(self, body: RequestResetBody) -> None:
        use_case: RequestPasswordResetUseCase = self.dependencies.resolve(
            RequestPasswordResetUseCase
        )

        await use_case.execute(
            RequestPasswordResetUseCase.Request(
                email=body.email,
            )
        )

    class ResetPasswordBody(BaseModel):
        reset_password_token: str
        new_password: str

    async def post(self, body: ResetPasswordBody) -> None:
        use_case: ResetPasswordUseCase = self.dependencies.resolve(ResetPasswordUseCase)

        await use_case.execute(
            ResetPasswordUseCase.Request(
                reset_password_token=body.reset_password_token,
                new_password=body.new_password,
            )
        )

    def register_routes(self) -> None:
        PREFIX: str = "/auth/reset_password"

        self._register_post_route(f"{PREFIX}/request", method=self.post_request)
        self._register_post_route(f"{PREFIX}", method=self.post)
