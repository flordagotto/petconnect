from bounded_contexts.auth.exceptions import AccountNotFoundByEmailException
from bounded_contexts.auth.use_cases import RequestPasswordResetUseCase
from common.testing import BaseUseCaseTest
from common.testing.base_testing_utils import BaseTestingUtils
from infrastructure.crypto import HashUtils
from infrastructure.uow_abstraction import make_unit_of_work


class TestRequestPasswordReset(BaseUseCaseTest, BaseTestingUtils):
    TEST_EMAIL: str = "test@test.com"
    TEST_PASSWORD: str = "test_password"

    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)
        self.use_case: RequestPasswordResetUseCase = self.dependencies.resolve(
            RequestPasswordResetUseCase
        )
        self.hash_utils: HashUtils = self.dependencies.resolve(HashUtils)

    async def test_request_password_reset(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            user = await self.create_profile(
                uow=uow,
            )

        await self.use_case.execute(
            RequestPasswordResetUseCase.Request(
                email=user.email,
            )
        )

    async def test_request_password_reset_fails(self) -> None:
        with self.assertRaises(AccountNotFoundByEmailException):
            await self.use_case.execute(
                RequestPasswordResetUseCase.Request(
                    email="non_existant_mail@test.com",
                )
            )
