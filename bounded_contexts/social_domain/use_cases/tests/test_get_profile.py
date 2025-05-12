from bounded_contexts.social_domain.enum import ProfileTypes
from bounded_contexts.social_domain.use_cases import GetProfileUseCase
from common.testing import BaseUseCaseTest
from common.testing.base_testing_utils import (
    BaseTestingUtils,
    ProfileData,
    OrganizationalProfileData,
)
from infrastructure.uow_abstraction import unit_of_work, UnitOfWork, make_unit_of_work


class TestGetProfile(BaseUseCaseTest, BaseTestingUtils):
    @unit_of_work
    async def initial_data(self, uow: UnitOfWork) -> None:
        self.personal_profile: ProfileData = await self.create_profile(
            uow=uow,
        )

        self.organizational_profile: OrganizationalProfileData = (
            await self.create_organizational_profile(uow=uow)
        )

    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.use_case: GetProfileUseCase = self.dependencies.resolve(GetProfileUseCase)

        await self.initial_data()

    async def test_get_personal_profile(self) -> None:
        view = await self.use_case.execute(
            GetProfileUseCase.Request(
                account_id=self.personal_profile.account_id,
            )
        )

        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            profile = await self.profile_service.get_profile(
                uow=uow, entity_id=self.personal_profile.profile_id
            )

            self.assertEqual(ProfileTypes.PERSONAL_PROFILE.value, view.profile_type)

            self.assertEqual(view.account_id, profile.account.entity_id)
            self.assertEqual(view.first_name, profile.first_name)
            self.assertEqual(view.surname, profile.surname)
            self.assertEqual(view.phone_number, profile.phone_number)
            self.assertEqual(view.government_id, profile.government_id)
            self.assertEqual(view.birthdate, profile.birthdate)
            self.assertEqual(view.profile_type, profile.profile_type.value)
            self.assertEqual(view.email, profile.account.email)

    async def test_get_organizational_profile(self) -> None:
        view = await self.use_case.execute(
            GetProfileUseCase.Request(
                account_id=self.organizational_profile.profile_data.account_id,
            )
        )

        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            profile = await self.profile_service.get_organizational_profile(
                uow=uow, entity_id=self.organizational_profile.profile_data.profile_id
            )

            self.assertEqual(
                ProfileTypes.ORGANIZATIONAL_PROFILE.value, view.profile_type
            )

            self.assertEqual(view.account_id, profile.account.entity_id)
            self.assertEqual(view.first_name, profile.first_name)
            self.assertEqual(view.surname, profile.surname)
            self.assertEqual(view.phone_number, profile.phone_number)
            self.assertEqual(view.government_id, profile.government_id)
            self.assertEqual(view.birthdate, profile.birthdate)
            self.assertEqual(view.profile_type, profile.profile_type.value)
            self.assertEqual(view.organization_id, profile.organization_id)
            self.assertEqual(view.organization_role, profile.organization_role.value)
            self.assertEqual(view.email, profile.account.email)
