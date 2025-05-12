from bounded_contexts.auth.exceptions import (
    DecodeTokenException,
    UnexpectedTokenException,
)
from bounded_contexts.auth.use_cases.reset_password import ResetPasswordUseCase
from bounded_contexts.auth.use_cases.tests.base_auth_testing_utils import (
    BaseAuthTestingUtils,
    AccountData,
)
from bounded_contexts.auth.value_objects import TokenData
from common.testing import BaseUseCaseTest
from infrastructure.crypto import HashUtils, TokenUtils
from infrastructure.uow_abstraction import unit_of_work, UnitOfWork, make_unit_of_work


class TestResetPassword(BaseUseCaseTest, BaseAuthTestingUtils):
    TEST_EMAIL: str = "test_email@test.com"
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

        self.use_case: ResetPasswordUseCase = self.dependencies.resolve(
            ResetPasswordUseCase
        )
        self.hash_utils: HashUtils = self.dependencies.resolve(HashUtils)
        self.token_utils: TokenUtils[TokenData] = self.dependencies.resolve(
            TokenUtils[TokenData]
        )

        await self.initial_data()

    async def test_reset_password(self) -> None:
        # Verify old password is set

        self.assertTrue(
            await self.hash_utils.verify_hash(
                hash_to_verify=self.user.password,
                string_to_verify=self.TEST_PASSWORD,
            )
        )

        # Rest password

        NEW_PASSWORD: str = "new_password"

        await self.use_case.execute(
            ResetPasswordUseCase.Request(
                reset_password_token=await self.accounts_service.generate_password_reset_token(
                    account_id=self.user.account_id,
                ),
                new_password=NEW_PASSWORD,
            )
        )

        # Get new data from db and verify that password changed

        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            user_data: AccountData = await self.get_account_by_id(
                uow=uow,
                account_id=self.user.account_id,
            )

        self.assertTrue(
            await self.hash_utils.verify_hash(
                hash_to_verify=user_data.password,
                string_to_verify=NEW_PASSWORD,
            )
        )

    async def test_decode_error_on_bad_token(self) -> None:
        with self.assertRaises(DecodeTokenException):
            await self.use_case.execute(
                ResetPasswordUseCase.Request(
                    reset_password_token="bad_token",
                    new_password="test",
                )
            )

    async def test_domain_error_on_wrong_token(self) -> None:
        with self.assertRaises(UnexpectedTokenException):
            await self.use_case.execute(
                ResetPasswordUseCase.Request(
                    reset_password_token=await self.accounts_service.generate_login_token(
                        account_id=self.user.account_id,
                    ),
                    new_password="test",
                )
            )
