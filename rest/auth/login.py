from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from bounded_contexts.auth.use_cases import LoginUseCase
from bounded_contexts.auth.views import TokenView
from infrastructure.rest import BaseAPIController


class LoginController(BaseAPIController):
    # OpenAPI standard:
    async def post(
        self, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
    ) -> TokenView:
        login_use_case: LoginUseCase = self.dependencies.resolve(LoginUseCase)

        return await login_use_case.execute(
            LoginUseCase.Request(
                email=form_data.username,
                password=form_data.password,
            )
        )

    def register_routes(self) -> None:
        PREFIX: str = "/auth/login"

        self._register_post_route(f"{PREFIX}", method=self.post)
