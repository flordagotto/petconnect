from infrastructure.rest import BaseAPIController
from rest import RouteManager
from rest.auth import LoginController, VerifyAccountController
from rest.auth.reset_password import ResetPasswordController


class AuthRouteManager(RouteManager):
    def _create_controllers(self) -> list[BaseAPIController]:
        login_route: LoginController = LoginController(dependencies=self.dependencies)
        verify_account: VerifyAccountController = VerifyAccountController(
            dependencies=self.dependencies
        )
        reset_password: ResetPasswordController = ResetPasswordController(
            dependencies=self.dependencies
        )

        return [login_route, verify_account, reset_password]
