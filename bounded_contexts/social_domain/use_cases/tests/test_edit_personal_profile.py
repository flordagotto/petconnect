import datetime
from bounded_contexts.social_domain.exceptions import ProfileNotFoundException
from bounded_contexts.social_domain.services.profile_service import ModifyProfileData
from bounded_contexts.social_domain.use_cases import EditPersonalProfileUseCase
from bounded_contexts.social_domain.views import PersonalProfileView
from common.testing import BaseUseCaseTest
from common.testing.base_testing_utils import BaseTestingUtils, PersonalProfileData
from infrastructure.uow_abstraction import make_unit_of_work, UnitOfWork, unit_of_work


class TestEditPersonalProfile(BaseUseCaseTest, BaseTestingUtils):
    @unit_of_work
    async def initial_data(self, uow: UnitOfWork) -> None:
        self.profile = await self.create_profile(uow=uow)

    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.use_case: EditPersonalProfileUseCase = self.dependencies.resolve(
            EditPersonalProfileUseCase
        )

        await self.initial_data()

    async def test_edit_personal_profile_success(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            profile_data: PersonalProfileData = await self.get_personal_profile(
                uow=uow, profile_id=self.profile.profile_id
            )

        new_profile_data = ModifyProfileData(
            entity_id=self.profile.profile_id,
            first_name="new first name",
            surname="new surname",
            phone_number=profile_data.phone_number,
            government_id=profile_data.government_id,
            birthdate=profile_data.birth_date,
            social_media_url="www.instagram.com/new_profile",
        )

        view: PersonalProfileView = await self.use_case.execute(
            EditPersonalProfileUseCase.Request(
                account_id=self.profile.account_id,
                profile_data=new_profile_data,
            )
        )

        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            self.assertEqual(
                PersonalProfileData(
                    entity_id=view.entity_id,
                    first_name=view.first_name,
                    surname=view.surname,
                    phone_number=view.phone_number,
                    government_id=view.government_id,
                    birth_date=view.birthdate,
                    social_media_url=view.social_media_url,
                ),
                await self.get_personal_profile(
                    uow=uow, profile_id=self.profile.profile_id
                ),
            )

    async def test_edit_no_profile_fails(self) -> None:
        new_profile_data = ModifyProfileData(
            entity_id=self.profile.profile_id,
            first_name="new first name",
            surname="new surname",
            phone_number="phone_number",
            government_id="government_id",
            birthdate=datetime.date(2020, 1, 1),
            social_media_url="www.instagram.com/new_profile",
        )

        with self.assertRaises(ProfileNotFoundException):
            await self.use_case.execute(
                EditPersonalProfileUseCase.Request(
                    account_id="12345",
                    profile_data=new_profile_data,
                )
            )
