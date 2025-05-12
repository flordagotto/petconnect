from bounded_contexts.social_domain.entities import Organization
from bounded_contexts.social_domain.services.organization_service import (
    OrganizationService,
)
from bounded_contexts.social_domain.use_cases import GetOrganizationsUseCase
from bounded_contexts.social_domain.views import OrganizationListView
from common.testing import BaseUseCaseTest
from common.testing.base_testing_utils import BaseTestingUtils
from infrastructure.uow_abstraction import unit_of_work, UnitOfWork


class TestGetOrganizationsUseCase(BaseUseCaseTest, BaseTestingUtils):
    TEST_NO_LIMIT = None
    TEST_OFFSET_ZERO = 0
    TEST_LIMIT = 2
    TEST_OFFSET = 1
    TEST_EMAIL_1 = "prueba1@gmail.com"
    TEST_EMAIL_2 = "prueba2@gmail.com"
    TEST_EMAIL_3 = "prueba3@gmail.com"
    TEST_ORGANIZATION_NAME_1 = "prueba1"
    TEST_ORGANIZATION_NAME_2 = "prueba2"
    TEST_ORGANIZATION_NAME_3 = "prueba3"

    @unit_of_work
    async def initial_data(self, uow: UnitOfWork) -> None:
        organization1 = await self.create_organization(
            uow=uow,
            account_email=self.TEST_EMAIL_1,
            organization_name=self.TEST_ORGANIZATION_NAME_1,
        )
        organization2 = await self.create_organization(
            uow=uow,
            account_email=self.TEST_EMAIL_2,
            organization_name=self.TEST_ORGANIZATION_NAME_2,
        )
        organization3 = await self.create_organization(
            uow=uow,
            account_email=self.TEST_EMAIL_3,
            organization_name=self.TEST_ORGANIZATION_NAME_3,
        )

        organizations_not_ordered: list[Organization] = [
            organization1,
            organization3,
            organization2,
        ]
        self.organizations = sorted(
            organizations_not_ordered,
            key=lambda organization: organization.organization_name,
        )

    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.use_case: GetOrganizationsUseCase = self.dependencies.resolve(
            GetOrganizationsUseCase
        )
        self.organizations_service = self.dependencies.resolve(OrganizationService)

        await self.initial_data()

    async def test_get_organizations_success(self) -> None:
        list_view: OrganizationListView = await self.use_case.execute(
            GetOrganizationsUseCase.Request(
                limit=self.TEST_NO_LIMIT, offset=self.TEST_OFFSET_ZERO
            )
        )

        self.assertEqual(len(self.organizations), list_view.total_count)

        for i in range(len(list_view.items)):
            self.assertEqual(
                (
                    self.organizations[i].entity_id,
                    self.organizations[i].organization_name,
                    self.organizations[i].creator_account_id,
                    self.organizations[i].verified,
                ),
                (
                    list_view.items[i].entity_id,
                    list_view.items[i].organization_name,
                    list_view.items[i].creator_account_id,
                    list_view.items[i].verified,
                ),
            )

    async def test_get_organizations_pagination_with_limit(self) -> None:
        list_view: OrganizationListView = await self.use_case.execute(
            GetOrganizationsUseCase.Request(
                limit=self.TEST_LIMIT, offset=self.TEST_OFFSET_ZERO
            )
        )

        self.assertEqual(len(self.organizations), list_view.total_count)
        self.assertEqual(self.TEST_LIMIT, len(list_view.items))

        for i in range(self.TEST_LIMIT):
            self.assertEqual(
                (
                    self.organizations[i].entity_id,
                    self.organizations[i].organization_name,
                    self.organizations[i].creator_account_id,
                    self.organizations[i].verified,
                ),
                (
                    list_view.items[i].entity_id,
                    list_view.items[i].organization_name,
                    list_view.items[i].creator_account_id,
                    list_view.items[i].verified,
                ),
            )

    async def test_get_organizations_pagination_with_offset(self) -> None:
        list_view: OrganizationListView = await self.use_case.execute(
            GetOrganizationsUseCase.Request(limit=None, offset=self.TEST_OFFSET)
        )

        self.assertEqual(len(self.organizations), list_view.total_count)
        index_offset = self.TEST_OFFSET

        for organization in list_view.items:
            self.assertEqual(
                (
                    self.organizations[index_offset].entity_id,
                    self.organizations[index_offset].organization_name,
                    self.organizations[index_offset].creator_account_id,
                    self.organizations[index_offset].verified,
                ),
                (
                    organization.entity_id,
                    organization.organization_name,
                    organization.creator_account_id,
                    organization.verified,
                ),
            )
            index_offset += 1
