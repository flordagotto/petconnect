from bounded_contexts.social_domain.enum import OrganizationRoles
from bounded_contexts.social_domain.exceptions import (
    AcceptOrganizationMemberUnauthorizedException,
    DisableOrganizationMemberUnauthorizedException,
)
from bounded_contexts.social_domain.use_cases import (
    EditOrganizationMemberStatus,
)
from bounded_contexts.social_domain.use_cases.tests.base_social_test_utils import (
    BaseSocialTestUtils,
    OrganizationAdminData,
    OrganizationMemberData,
)
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work, make_unit_of_work


class TestEditOrganizationMemberStatus(
    BaseSocialTestUtils,
):
    @unit_of_work
    async def initial_data(self, uow: UnitOfWork) -> None:
        self.organization_admin_data: OrganizationAdminData = (
            await self.create_organization(
                uow=uow,
            )
        )

        self.collaborator: OrganizationMemberData = (
            await self.create_organizational_profile(
                uow=uow,
                email=f"collaborator-{self.TEST_EMAIL}",
                organization_id=self.organization_admin_data.organization_id,
                organization_role=OrganizationRoles.COLLABORATOR,
            )
        )

        self.manager: OrganizationMemberData = await self.create_organizational_profile(
            uow=uow,
            email=f"manager-{self.TEST_EMAIL}",
            organization_id=self.organization_admin_data.organization_id,
            organization_role=OrganizationRoles.MANAGER,
        )

    async def setUp(self) -> None:
        await BaseSocialTestUtils.setUp(self)

        self.use_case: EditOrganizationMemberStatus = self.dependencies.resolve(
            EditOrganizationMemberStatus
        )

        await self.initial_data()

    async def test_non_admin_cant_accept_status(self) -> None:
        for member_account_id, accepted in zip(
            [
                self.collaborator.account_id,
                self.manager.account_id,
            ],
            [True, False],
        ):
            raised_exception = (
                AcceptOrganizationMemberUnauthorizedException
                if accepted
                else DisableOrganizationMemberUnauthorizedException
            )

            with self.assertRaises(raised_exception):
                await self.use_case.execute(
                    EditOrganizationMemberStatus.Request(
                        actor_account_id=self.collaborator.account_id,
                        member_account_id=member_account_id,
                        accepted=accepted,
                    )
                )

    async def test_other_org_admin_cant_accept(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            other_organization_admin: OrganizationAdminData = (
                await self.create_organization(
                    uow=uow,
                    email=f"other-admin-{self.TEST_EMAIL}",
                    organization_name="Other Organization",
                )
            )

        for member_account_id, accepted in zip(
            [
                self.collaborator.account_id,
                self.manager.account_id,
            ],
            [True, False],
        ):
            raised_exception = (
                AcceptOrganizationMemberUnauthorizedException
                if accepted
                else DisableOrganizationMemberUnauthorizedException
            )

            with self.assertRaises(raised_exception):
                await self.use_case.execute(
                    EditOrganizationMemberStatus.Request(
                        actor_account_id=other_organization_admin.account_id,
                        member_account_id=member_account_id,
                        accepted=accepted,
                    )
                )

    async def test_approve_and_disable_member(self) -> None:
        for member_account_id in [
            self.collaborator.account_id,
            self.manager.account_id,
        ]:
            async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
                organizational_profile = (
                    await self.profile_service.get_organizational_profile_by_account_id(
                        uow=uow,
                        account_id=member_account_id,
                    )
                )

                self.assertFalse(organizational_profile.verified_by_organization)

            await self.use_case.execute(
                EditOrganizationMemberStatus.Request(
                    actor_account_id=self.organization_admin_data.account_id,
                    member_account_id=member_account_id,
                    accepted=True,
                )
            )

            async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
                organizational_profile = (
                    await self.profile_service.get_organizational_profile_by_account_id(
                        uow=uow,
                        account_id=member_account_id,
                    )
                )

                self.assertTrue(organizational_profile.verified_by_organization)

            await self.use_case.execute(
                EditOrganizationMemberStatus.Request(
                    actor_account_id=self.organization_admin_data.account_id,
                    member_account_id=member_account_id,
                    accepted=False,
                )
            )

            async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
                organizational_profile = (
                    await self.profile_service.get_organizational_profile_by_account_id(
                        uow=uow,
                        account_id=member_account_id,
                    )
                )

                self.assertFalse(organizational_profile.verified_by_organization)
