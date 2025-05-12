from bounded_contexts.auth.exceptions import (
    IncorrectLoginDataException,
    AccountNotFoundByEmailException,
    AccountNotVerifiedException,
)
from bounded_contexts.auth.use_cases import LoginUseCase
from bounded_contexts.auth.use_cases.tests.base_auth_testing_utils import (
    BaseAuthTestingUtils,
    AccountData,
)
from bounded_contexts.auth.value_objects import TokenData
from bounded_contexts.auth.views import TokenView
from common.testing import BaseUseCaseTest
from infrastructure.crypto import TokenUtils
from infrastructure.uow_abstraction import unit_of_work, UnitOfWork, make_unit_of_work


class TestLoginUseCase(BaseUseCaseTest, BaseAuthTestingUtils):
    TEST_EMAIL: str = "test_EMAIL@test.com"
    TEST_PASSWORD: str = "test_password"

    @unit_of_work
    async def initial_data(self, uow: UnitOfWork) -> None:
        self.user: AccountData = await self.create_account(
            uow=uow,
            email=self.TEST_EMAIL,
            password=self.TEST_PASSWORD,
        )

    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.use_case: LoginUseCase = self.dependencies.resolve(LoginUseCase)
        self.token_utils: TokenUtils[TokenData] = self.dependencies.resolve(
            TokenUtils[TokenData]
        )

        await self.initial_data()

    async def test_login_success(self) -> None:
        view: TokenView = await self.use_case.execute(
            LoginUseCase.Request(
                email=self.TEST_EMAIL,
                password=self.TEST_PASSWORD,
            )
        )

        token_payload: TokenData = await self.token_utils.decode_token(
            token=view.access_token,
        )

        self.assertEqual(token_payload.account_id, self.user.account_id)

    async def test_login_wrong_password(self) -> None:
        with self.assertRaises(IncorrectLoginDataException):
            await self.use_case.execute(
                LoginUseCase.Request(
                    email=self.TEST_EMAIL,
                    password="wrong_password",
                )
            )

    async def test_login_wrong_mail(self) -> None:
        with self.assertRaises(AccountNotFoundByEmailException):
            await self.use_case.execute(
                LoginUseCase.Request(
                    email="wrong_email@test.com",
                    password="test_password!",
                )
            )

    async def test_login_unverified_account(self) -> None:
        unverified_email: str = "unverified_account@test.com"

        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            await self.create_account(
                uow=uow,
                email=unverified_email,
                password=self.TEST_PASSWORD,
                auto_verify=False,
            )

        with self.assertRaises(AccountNotVerifiedException):
            await self.use_case.execute(
                LoginUseCase.Request(
                    email=unverified_email,
                    password=self.TEST_PASSWORD,
                )
            )
