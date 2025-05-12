from bounded_contexts.auth.exceptions import (
    AccountAlreadyVerifiedException,
    AccountNotFoundByEmailException,
)
from bounded_contexts.auth.use_cases import ResendVerificationRequest
from bounded_contexts.auth.use_cases.tests.base_auth_testing_utils import (
    BaseAuthTestingUtils,
    AccountData,
)
from common.testing import BaseUseCaseTest
from infrastructure.crypto import HashUtils
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work, make_unit_of_work


class TestResendVerificationRequest(BaseUseCaseTest, BaseAuthTestingUtils):
    TEST_EMAIL: str = "test@test.com"
    TEST_PASSWORD: str = "test_password"

    @unit_of_work
    async def initial_data(self, uow: UnitOfWork) -> None:
        self.user: AccountData = await self.create_account(
            uow=uow,
            email=self.TEST_EMAIL,
            password=self.TEST_PASSWORD,
            auto_verify=False,
        )

    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)
        self.use_case: ResendVerificationRequest = self.dependencies.resolve(
            ResendVerificationRequest
        )
        self.hash_utils: HashUtils = self.dependencies.resolve(HashUtils)
        await self.initial_data()

    async def test_request_password_reset(self) -> None:
        await self.use_case.execute(
            ResendVerificationRequest.Request(
                email=self.user.email,
            )
        )

    async def test_request_password_reset_fails_on_already_verified_account(
        self,
    ) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            verified_user: AccountData = await self.create_account(
                uow=uow,
                email="test_mail_already_verified@test.com",
                password=self.TEST_PASSWORD,
                auto_verify=True,
            )

        with self.assertRaises(AccountAlreadyVerifiedException):
            await self.use_case.execute(
                ResendVerificationRequest.Request(
                    email=verified_user.email,
                )
            )

    async def test_account_not_found(self) -> None:
        with self.assertRaises(AccountNotFoundByEmailException):
            await self.use_case.execute(
                ResendVerificationRequest.Request(
                    email="thisemailisnotregistered@test.com",
                )
            )
