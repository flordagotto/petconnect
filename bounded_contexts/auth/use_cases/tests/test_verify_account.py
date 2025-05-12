from bounded_contexts.auth.entities import Account
from bounded_contexts.auth.exceptions import (
    DecodeTokenException,
    UnexpectedTokenException,
)
from bounded_contexts.auth.use_cases import VerifyAccountUseCase
from bounded_contexts.auth.use_cases.tests.base_auth_testing_utils import (
    BaseAuthTestingUtils,
    AccountData,
)
from common.testing import BaseUseCaseTest
from infrastructure.uow_abstraction import unit_of_work, UnitOfWork, make_unit_of_work


class TestVerifyAccountUseCase(BaseUseCaseTest, BaseAuthTestingUtils):
    TEST_EMAIL: str = "test_email@test.com"
    TEST_PASSWORD: str = "test_password"

    @unit_of_work
    async def initial_data(self, uow: UnitOfWork) -> None:
        self.user: AccountData = await self.create_account(
            uow=uow,
            email=self.TEST_EMAIL,
            password=self.TEST_PASSWORD,
            auto_verify=False,
        )

        self.verify_account_token: str = (
            await self.accounts_service.generate_account_verification_token(
                account_id=self.user.account_id,
            )
        )

    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.use_case: VerifyAccountUseCase = self.dependencies.resolve(
            VerifyAccountUseCase
        )

        await self.initial_data()

    async def test_verify_account(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            account: Account = await self.accounts_service.get_account_by_id(
                uow=uow,
                account_id=self.user.account_id,
            )

            self.assertEqual(account.verified, False)

        await self.use_case.execute(
            VerifyAccountUseCase.Request(
                verification_token=self.verify_account_token,
            )
        )

        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            account = await self.accounts_service.get_account_by_id(
                uow=uow,
                account_id=self.user.account_id,
            )

            self.assertEqual(account.verified, True)

    async def test_non_parsable_token(self) -> None:
        with self.assertRaises(DecodeTokenException):
            await self.use_case.execute(
                VerifyAccountUseCase.Request(
                    verification_token="wrong_token",
                )
            )

    async def test_invalid_token(self) -> None:
        with self.assertRaises(UnexpectedTokenException):
            await self.use_case.execute(
                VerifyAccountUseCase.Request(
                    verification_token=await self.accounts_service.generate_login_token(
                        account_id=self.user.account_id,
                    ),
                )
            )
