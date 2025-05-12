from bounded_contexts.auth.exceptions import EmailAlreadyRegisteredException
from bounded_contexts.auth.use_cases import CreateAccountUseCase
from bounded_contexts.auth.use_cases.tests.base_auth_testing_utils import (
    BaseAuthTestingUtils,
    AccountData,
)
from bounded_contexts.auth.views import AccountView
from common.testing import BaseUseCaseTest
from infrastructure.crypto import HashUtils
from infrastructure.uow_abstraction import make_unit_of_work


class TestCreateAccount(BaseUseCaseTest, BaseAuthTestingUtils):
    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)
        self.use_case: CreateAccountUseCase = self.dependencies.resolve(
            CreateAccountUseCase
        )
        self.hash_utils: HashUtils = self.dependencies.resolve(HashUtils)

    async def test_create_account_success(self) -> None:
        view: AccountView = await self.use_case.execute(
            CreateAccountUseCase.Request(
                email="test_email@test.com",
                password="test_password",
            )
        )

        self.assertEqual(
            "test_email@test.com",
            view.email,
        )

        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            user: AccountData = await self.get_account_by_id(
                uow=uow, account_id=view.entity_id
            )

            self.assertTrue(
                await self.hash_utils.verify_hash("test_password", user.password)
            )

    async def test_create_account_already_existing_mail(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            await self.create_account(
                uow=uow, email="test@test.com", password="test_password"
            )

        with self.assertRaises(EmailAlreadyRegisteredException):
            await self.use_case.execute(
                CreateAccountUseCase.Request(
                    email="test@test.com",
                    password="test_password",
                )
            )
