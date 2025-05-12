from bounded_contexts.social_domain.enum import OrganizationRoles
from bounded_contexts.social_domain.exceptions import (
    ViewOrganizationalProfilesUnauthorizedException,
)
from bounded_contexts.social_domain.use_cases import GetOrganizationProfilesUseCase
from bounded_contexts.social_domain.use_cases.tests.base_social_test_utils import (
    BaseSocialTestUtils,
    OrganizationAdminData,
    OrganizationMemberData,
)
from bounded_contexts.social_domain.views import (
    PaginationFriendlyOrganizationalProfileView,
)
from infrastructure.uow_abstraction import unit_of_work, UnitOfWork


class TestGetOrganizationProfiles(
    BaseSocialTestUtils,
):
    @unit_of_work
    async def initial_data(self, uow: UnitOfWork) -> None:
        self.organization_admin_data: OrganizationAdminData = (
            await self.create_organization(
                uow=uow,
            )
        )

        self.collaborators: list[OrganizationMemberData] = []
        self.managers: list[OrganizationMemberData] = []

        for i in range(10):
            collaborator: OrganizationMemberData = (
                await self.create_organizational_profile(
                    uow=uow,
                    email=f"collaborator-{str(i)}-{self.TEST_EMAIL}",
                    organization_id=self.organization_admin_data.organization_id,
                    organization_role=OrganizationRoles.COLLABORATOR,
                )
            )

            manager: OrganizationMemberData = await self.create_organizational_profile(
                uow=uow,
                email=f"manager-{str(i)}-{self.TEST_EMAIL}",
                organization_id=self.organization_admin_data.organization_id,
                organization_role=OrganizationRoles.MANAGER,
            )

            self.collaborators.append(collaborator)
            self.managers.append(manager)

    async def setUp(self) -> None:
        await BaseSocialTestUtils.setUp(self)

        self.use_case: GetOrganizationProfilesUseCase = self.dependencies.resolve(
            GetOrganizationProfilesUseCase
        )

        await self.initial_data()

    async def test_get_organization_profiles(self) -> None:
        request = GetOrganizationProfilesUseCase.Request(
            actor_account_id=self.organization_admin_data.account_id,
        )

        response: PaginationFriendlyOrganizationalProfileView = (
            await self.use_case.execute(request=request)
        )

        self.assertEqual(response.total_count, 20)
        self.assertEqual(len(response.items), 20)

        self.assertEqual(
            set([profile.account_id for profile in self.managers + self.collaborators]),
            set([profile.account_id for profile in response.items]),
        )

    async def test_other_users_are_unauthorized(self) -> None:
        for actor_account_id in [
            self.collaborators[0].account_id,
            self.managers[0].account_id,
        ]:
            with self.assertRaises(ViewOrganizationalProfilesUnauthorizedException):
                request = GetOrganizationProfilesUseCase.Request(
                    actor_account_id=actor_account_id,
                )

                await self.use_case.execute(request=request)
