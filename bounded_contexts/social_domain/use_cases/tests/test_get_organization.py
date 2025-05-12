from bounded_contexts.social_domain.entities import Organization
from bounded_contexts.social_domain.exceptions import OrganizationNotFoundByIdException
from bounded_contexts.social_domain.services.organization_service import (
    OrganizationService,
)
from bounded_contexts.social_domain.use_cases import GetOrganizationUseCase
from common.testing import BaseUseCaseTest
from common.testing.base_testing_utils import BaseTestingUtils
from infrastructure.uow_abstraction import unit_of_work, UnitOfWork, make_unit_of_work


class TestGetOrganizationUseCase(BaseUseCaseTest, BaseTestingUtils):
    TEST_ORGANIZATION_ID = "123456"
    TEST_EMAIL = "prueba@gmail.com"
    TEST_ORGANIZATION_NAME = "prueba"

    @unit_of_work
    async def initial_data(self, uow: UnitOfWork) -> None:
        self.organization = await self.create_organization(
            uow=uow,
            account_email=self.TEST_EMAIL,
            organization_name=self.TEST_ORGANIZATION_NAME,
        )

    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.use_case: GetOrganizationUseCase = self.dependencies.resolve(
            GetOrganizationUseCase
        )
        self.organizations_service = self.dependencies.resolve(OrganizationService)

        await self.initial_data()

    async def test_get_organization_success(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            organization: Organization = (
                await self.organizations_service.get_organization_by_id(
                    uow=uow, entity_id=self.organization.entity_id
                )
            )

            self.assertEqual(
                (
                    self.organization.entity_id,
                    self.organization.organization_name,
                    self.organization.creator_account_id,
                    self.organization.verified,
                ),
                (
                    organization.entity_id,
                    organization.organization_name,
                    organization.creator_account_id,
                    organization.verified,
                ),
            )

    async def test_get_organization_fails(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            with self.assertRaises(OrganizationNotFoundByIdException):
                await self.organizations_service.get_organization_by_id(
                    uow=uow, entity_id=self.TEST_ORGANIZATION_ID
                )
