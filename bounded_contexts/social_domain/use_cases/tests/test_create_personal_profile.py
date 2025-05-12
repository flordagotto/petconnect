from bounded_contexts.auth.exceptions import EmailAlreadyRegisteredException
from bounded_contexts.auth.use_cases import CreateAccountUseCase
from bounded_contexts.auth.use_cases.tests.base_auth_testing_utils import (
    BaseAuthTestingUtils,
)
from bounded_contexts.social_domain.entities import PersonalProfile
from bounded_contexts.social_domain.services.profile_service import ProfileService
from bounded_contexts.social_domain.use_cases import CreatePersonalProfileUseCase
from bounded_contexts.social_domain.views import PersonalProfileView
from common.testing import BaseUseCaseTest
from infrastructure.date_utils import date_now
from infrastructure.uow_abstraction import make_unit_of_work


class TestCreatePersonalProfileUseCase(
    BaseUseCaseTest,
    BaseAuthTestingUtils,
):
    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.use_case: CreatePersonalProfileUseCase = self.dependencies.resolve(
            CreatePersonalProfileUseCase
        )
        self.profile_service = self.dependencies.resolve(ProfileService)

    async def test_create_personal_profile_success(self) -> None:
        view: PersonalProfileView = await self.use_case.execute(
            CreatePersonalProfileUseCase.Request(
                account_request=CreateAccountUseCase.Request(
                    email="gasparnoriega@hotmail.com",
                    password="test_password",
                ),
                first_name="gaspar",
                surname="noriega",
                phone_number="3512421500",
                birthdate=date_now(),
                government_id="40123123",
            )
        )

        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            user: PersonalProfile = await self.profile_service.get_personal_profile(
                uow=uow, entity_id=view.entity_id
            )

            self.assertEqual(
                (
                    view.entity_id,
                    view.account_id,
                    view.first_name,
                    view.surname,
                    view.phone_number,
                    view.profile_type,
                    view.birthdate,
                    view.government_id,
                ),
                (
                    user.entity_id,
                    user.account.entity_id,
                    user.first_name,
                    user.surname,
                    user.phone_number,
                    user.profile_type.value,
                    user.birthdate,
                    user.government_id,
                ),
            )

    async def test_email_already_registered(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            await self.create_account(
                uow=uow,
                email="gasparnoriega@hotmail.com",
                password="test_password",
            )

        with self.assertRaises(EmailAlreadyRegisteredException):
            await self.use_case.execute(
                CreatePersonalProfileUseCase.Request(
                    account_request=CreateAccountUseCase.Request(
                        email="gasparnoriega@hotmail.com",
                        password="test_password",
                    ),
                    first_name="gaspar",
                    surname="noriega",
                    phone_number="3512421500",
                    government_id="40123123",
                    birthdate=date_now(),
                )
            )
