from dataclasses import dataclass
from datetime import date

from bounded_contexts.auth.use_cases.tests.base_auth_testing_utils import (
    BaseAuthTestingUtils,
    AccountData,
)
from bounded_contexts.social_domain.enum import OrganizationRoles
from bounded_contexts.social_domain.services.organization_service import (
    OrganizationService,
)
from bounded_contexts.social_domain.services.profile_service import ProfileService
from common.testing import BaseUseCaseTest
from infrastructure.date_utils import date_now
from infrastructure.uow_abstraction import UnitOfWork


@dataclass
class OrganizationAdminData:
    account_id: str
    organization_id: str


@dataclass
class OrganizationMemberData:
    account_id: str
    organization_id: str
    organization_role: OrganizationRoles


class BaseSocialTestUtils(
    BaseUseCaseTest,
    BaseAuthTestingUtils,
):
    # Test org data
    TEST_ORGANIZATION_NAME: str = "Southern Paws"

    # Test admin data
    TEST_ADMIN_EMAIL = "test_admin_email@test.com"
    TEST_ADMIN_PASSWORD: str = "test_admin_password"
    TEST_ADMIN_FIRST_NAME: str = "admin name"
    TEST_ADMIN_SURNAME: str = "admin surname"
    TEST_ADMIN_PHONE_NUMBER: str = "1234567891234"
    TEST_ADMIN_GOV_ID: str = "1546345986345"

    # Test member data
    TEST_EMAIL = "test_email@test.com"
    TEST_PASSWORD: str = "test_password"
    TEST_FIRST_NAME: str = "member name"
    TEST_SURNAME: str = "member surname"
    TEST_PHONE_NUMBER: str = "53639456"
    TEST_GOV_ID: str = "1045"

    async def create_organizational_profile(
        self,
        uow: UnitOfWork,
        organization_id: str,
        organization_role: OrganizationRoles,
        email: str = TEST_EMAIL,
        password: str = TEST_PASSWORD,
        first_name: str = TEST_FIRST_NAME,
        surname: str = TEST_SURNAME,
        phone_number: str = TEST_PHONE_NUMBER,
        government_id: str = TEST_GOV_ID,
        birthdate: date = date_now(),
        auto_verify: bool = True,
    ) -> OrganizationMemberData:
        member_account_data: AccountData = await self.create_account(
            uow=uow,
            email=email,
            password=password,
            auto_verify=auto_verify,
        )

        await self.profile_service.create_organization_employee_profile(
            uow=uow,
            account=await self.accounts_service.get_account_by_id(
                uow=uow, account_id=member_account_data.account_id
            ),
            first_name=first_name,
            surname=surname,
            phone_number=phone_number,
            government_id=government_id,
            birthdate=birthdate,
            organization_id=organization_id,
            organization_role=organization_role,
        )

        return OrganizationMemberData(
            account_id=member_account_data.account_id,
            organization_id=organization_id,
            organization_role=organization_role,
        )

    async def create_organization(
        self,
        uow: UnitOfWork,
        email: str = TEST_ADMIN_EMAIL,
        password: str = TEST_ADMIN_PASSWORD,
        first_name: str = TEST_ADMIN_FIRST_NAME,
        surname: str = TEST_ADMIN_SURNAME,
        phone_number: str = TEST_ADMIN_PHONE_NUMBER,
        government_id: str = TEST_ADMIN_GOV_ID,
        organization_name: str = TEST_ORGANIZATION_NAME,
        birthdate: date = date_now(),
        auto_verify: bool = True,
    ) -> OrganizationAdminData:
        admin_account_data: AccountData = await self.create_account(
            uow=uow,
            email=email,
            password=password,
            auto_verify=auto_verify,
        )

        organization = await self.organization_service.create_organization(
            uow=uow,
            creator_account_id=admin_account_data.account_id,
            organization_name=organization_name,
            phone_number=phone_number,
        )

        await self.profile_service.create_organization_admin_profile(
            uow=uow,
            account=await self.accounts_service.get_account_by_id(
                uow=uow, account_id=admin_account_data.account_id
            ),
            first_name=first_name,
            surname=surname,
            phone_number=phone_number,
            government_id=government_id,
            birthdate=birthdate,
            organization_id=organization.entity_id,
        )

        return OrganizationAdminData(
            organization_id=organization.entity_id,
            account_id=admin_account_data.account_id,
        )

    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.profile_service = self.dependencies.resolve(ProfileService)
        self.organization_service = self.dependencies.resolve(OrganizationService)
