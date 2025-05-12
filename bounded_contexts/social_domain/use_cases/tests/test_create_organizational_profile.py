from bounded_contexts.social_domain.entities import OrganizationalProfile
from bounded_contexts.social_domain.enum import OrganizationRoles
from bounded_contexts.social_domain.exceptions import (
    RegisterOrganizationAdminUnauthorizedException,
)
from bounded_contexts.social_domain.use_cases import CreateOrganizationalProfileUseCase
from bounded_contexts.social_domain.use_cases.tests.base_social_test_utils import (
    BaseSocialTestUtils,
    OrganizationAdminData,
)
from bounded_contexts.social_domain.views import OrganizationalProfileView
from infrastructure.date_utils import date_now
from infrastructure.uow_abstraction import unit_of_work, UnitOfWork, make_unit_of_work


class TestCreateOrganizationalProfile(
    BaseSocialTestUtils,
):
    @unit_of_work
    async def initial_data(self, uow: UnitOfWork) -> None:
        self.organization_admin_data: OrganizationAdminData = (
            await self.create_organization(
                uow=uow,
            )
        )

    async def setUp(self) -> None:
        await BaseSocialTestUtils.setUp(self)

        self.use_case: CreateOrganizationalProfileUseCase = self.dependencies.resolve(
            CreateOrganizationalProfileUseCase
        )

        await self.initial_data()

    async def test_cant_register_admin(self) -> None:
        with self.assertRaises(RegisterOrganizationAdminUnauthorizedException):
            await self.use_case.execute(
                CreateOrganizationalProfileUseCase.Request(
                    email=self.TEST_EMAIL,
                    password=self.TEST_PASSWORD,
                    first_name=self.TEST_FIRST_NAME,
                    surname=self.TEST_SURNAME,
                    phone_number=self.TEST_PHONE_NUMBER,
                    government_id=self.TEST_GOV_ID,
                    birthdate=date_now(),
                    organization_id=self.organization_admin_data.organization_id,
                    organization_role=OrganizationRoles.ADMIN,
                )
            )

    async def test_create_organization_member(self) -> None:
        for role in [OrganizationRoles.COLLABORATOR, OrganizationRoles.MANAGER]:
            view: OrganizationalProfileView = await self.use_case.execute(
                CreateOrganizationalProfileUseCase.Request(
                    email=f"{role.value}-{self.TEST_EMAIL}",
                    password=self.TEST_PASSWORD,
                    first_name=self.TEST_FIRST_NAME,
                    surname=self.TEST_SURNAME,
                    phone_number=self.TEST_PHONE_NUMBER,
                    government_id=self.TEST_GOV_ID,
                    birthdate=date_now(),
                    organization_id=self.organization_admin_data.organization_id,
                    organization_role=role,
                )
            )

            async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
                user: OrganizationalProfile = (
                    await self.profile_service.get_organizational_profile(
                        uow=uow, entity_id=view.entity_id
                    )
                )

                self.assertEqual(role, user.organization_role)
                self.assertFalse(user.verified_by_organization)

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
