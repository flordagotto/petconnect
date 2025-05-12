from bounded_contexts.auth.entities import Account
from bounded_contexts.auth.exceptions import EmailAlreadyRegisteredException
from bounded_contexts.auth.services import AccountsService
from bounded_contexts.social_domain.entities import Organization
from bounded_contexts.social_domain.exceptions import (
    OrganizationAlreadyRegisteredException,
)
from bounded_contexts.social_domain.services.organization_service import (
    OrganizationService,
)
from bounded_contexts.social_domain.services.profile_service import ProfileService
from bounded_contexts.social_domain.use_cases import CreateOrganizationUseCase
from bounded_contexts.social_domain.views import OrganizationView
from common.testing import BaseUseCaseTest
from infrastructure.date_utils import date_now
from infrastructure.uow_abstraction import make_unit_of_work


class TestCreateOrganizationUseCase(BaseUseCaseTest):
    TEST_ACCOUNT_ID: str = "test_id"
    TEST_EMAIL = "test_email@test.com"
    TEST_PASSWORD: str = "test_password"
    TEST_FIRST_NAME: str = "name"
    TEST_SURNAME: str = "surname"
    TEST_PHONE_NUMBER: str = "12345"
    TEST_GOVERNMENT_ID: str = "1"
    TEST_ORGANIZATION_NAME: str = "patitas"

    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.use_case: CreateOrganizationUseCase = self.dependencies.resolve(
            CreateOrganizationUseCase
        )
        self.accounts_service = self.dependencies.resolve(AccountsService)
        self.profile_service = self.dependencies.resolve(ProfileService)
        self.organizations_service = self.dependencies.resolve(OrganizationService)

    async def test_create_organization_success(self) -> None:
        view: OrganizationView = await self.use_case.execute(
            CreateOrganizationUseCase.Request(
                organization_admin_request=CreateOrganizationUseCase.Request.OrganizationAdminRequest(
                    email=self.TEST_EMAIL,
                    password=self.TEST_PASSWORD,
                    first_name=self.TEST_FIRST_NAME,
                    surname=self.TEST_SURNAME,
                    phone_number=self.TEST_PHONE_NUMBER,
                    government_id=self.TEST_GOVERNMENT_ID,
                    birthdate=date_now(),
                ),
                organization_request=CreateOrganizationUseCase.Request.OrganizationRequest(
                    organization_name=self.TEST_ORGANIZATION_NAME,
                    phone_number=self.TEST_PHONE_NUMBER,
                ),
            )
        )

        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            organization: Organization = (
                await self.organizations_service.get_organization_by_name(
                    uow=uow,
                    organization_name=view.organization_name,
                )
            )

            account: Account = await self.accounts_service.get_account_by_email(
                uow=uow, email=self.TEST_EMAIL
            )

            self.assertEqual(
                (
                    organization.entity_id,
                    organization.organization_name,
                    organization.verified,
                    organization.phone_number,
                    organization.social_media_url,
                    account.entity_id,
                ),
                (
                    view.entity_id,
                    view.organization_name,
                    view.verified,
                    view.phone_number,
                    view.social_media_url,
                    view.creator_account_id,
                ),
            )

    async def test_create_organization_already_registered(self) -> None:
        await self.use_case.execute(
            CreateOrganizationUseCase.Request(
                organization_admin_request=CreateOrganizationUseCase.Request.OrganizationAdminRequest(
                    email=self.TEST_EMAIL,
                    password=self.TEST_PASSWORD,
                    first_name=self.TEST_FIRST_NAME,
                    surname=self.TEST_SURNAME,
                    phone_number=self.TEST_PHONE_NUMBER,
                    government_id=self.TEST_GOVERNMENT_ID,
                    birthdate=date_now(),
                ),
                organization_request=CreateOrganizationUseCase.Request.OrganizationRequest(
                    organization_name=self.TEST_ORGANIZATION_NAME,
                    phone_number=self.TEST_PHONE_NUMBER,
                ),
            )
        )

        with self.assertRaises(OrganizationAlreadyRegisteredException):
            await self.use_case.execute(
                CreateOrganizationUseCase.Request(
                    organization_admin_request=CreateOrganizationUseCase.Request.OrganizationAdminRequest(
                        email="new@email.com",
                        password=self.TEST_PASSWORD,
                        first_name=self.TEST_FIRST_NAME,
                        surname=self.TEST_SURNAME,
                        phone_number=self.TEST_PHONE_NUMBER,
                        government_id=self.TEST_GOVERNMENT_ID,
                        birthdate=date_now(),
                    ),
                    organization_request=CreateOrganizationUseCase.Request.OrganizationRequest(
                        organization_name=self.TEST_ORGANIZATION_NAME,
                        phone_number=self.TEST_PHONE_NUMBER,
                    ),
                )
            )

    async def test_create_organization_account_already_registered(self) -> None:
        await self.use_case.execute(
            CreateOrganizationUseCase.Request(
                organization_admin_request=CreateOrganizationUseCase.Request.OrganizationAdminRequest(
                    email=self.TEST_EMAIL,
                    password=self.TEST_PASSWORD,
                    first_name=self.TEST_FIRST_NAME,
                    surname=self.TEST_SURNAME,
                    phone_number=self.TEST_PHONE_NUMBER,
                    government_id=self.TEST_GOVERNMENT_ID,
                    birthdate=date_now(),
                ),
                organization_request=CreateOrganizationUseCase.Request.OrganizationRequest(
                    organization_name=self.TEST_ORGANIZATION_NAME,
                    phone_number=self.TEST_PHONE_NUMBER,
                ),
            )
        )

        with self.assertRaises(EmailAlreadyRegisteredException):
            await self.use_case.execute(
                CreateOrganizationUseCase.Request(
                    organization_admin_request=CreateOrganizationUseCase.Request.OrganizationAdminRequest(
                        email=self.TEST_EMAIL,
                        password=self.TEST_PASSWORD,
                        first_name=self.TEST_FIRST_NAME,
                        surname=self.TEST_SURNAME,
                        phone_number=self.TEST_PHONE_NUMBER,
                        government_id=self.TEST_GOVERNMENT_ID,
                        birthdate=date_now(),
                    ),
                    organization_request=CreateOrganizationUseCase.Request.OrganizationRequest(
                        organization_name=self.TEST_ORGANIZATION_NAME,
                        phone_number=self.TEST_PHONE_NUMBER,
                    ),
                )
            )
