from bounded_contexts.auth.use_cases import (
    CreateAccountUseCase,
    ResendVerificationRequest,
    RequestPasswordResetUseCase,
)
from bounded_contexts.social_domain.email import SocialEmailSubjects
from bounded_contexts.social_domain.event_handlers.profile_events_handler import (
    VerifyAccountUrls,
)
from bounded_contexts.social_domain.use_cases import (
    CreatePersonalProfileUseCase,
    CreateOrganizationUseCase,
    VerifyOrganizationUseCase,
)
from common.testing import BaseUseCaseTest
from common.testing.base_testing_utils import BaseTestingUtils
from infrastructure.date_utils import date_now
from infrastructure.email import BaseEmailGateway
from infrastructure.uow_abstraction import make_unit_of_work


class TestProfileRegisteredEventHandler(BaseUseCaseTest, BaseTestingUtils):
    TEST_EMAIL: str = "gasparnoriega@hotmail.com"
    TEST_PASSWORD: str = "test_password"
    TEST_FIRST_NAME: str = "name"
    TEST_SURNAME: str = "surname"
    TEST_PHONE_NUMBER: str = "12345"
    TEST_GOVERNMENT_ID: str = "1"
    TEST_ORGANIZATION_NAME: str = "patitas"
    TEST_SOCIAL_MEDIA_URL: str = "www.instagram.com/profile"

    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.create_personal_profile: CreatePersonalProfileUseCase = (
            self.dependencies.resolve(CreatePersonalProfileUseCase)
        )

        self.create_org_profile: CreateOrganizationUseCase = self.dependencies.resolve(
            CreateOrganizationUseCase
        )

        self.resend_verification_request_use_case = self.dependencies.resolve(
            ResendVerificationRequest
        )

        self.email_gateway: BaseEmailGateway = self.dependencies.resolve(
            BaseEmailGateway
        )

        self.request_password_reset_use_case = self.dependencies.resolve(
            RequestPasswordResetUseCase
        )

        self.verify_organization_use_case = self.dependencies.resolve(
            VerifyOrganizationUseCase
        )

        self.email_gateway.clear_cache()

    async def test_create_personal_profile_triggers_mail_sent(self) -> None:
        await self.create_personal_profile.execute(
            CreatePersonalProfileUseCase.Request(
                account_request=CreateAccountUseCase.Request(
                    email=self.TEST_EMAIL,
                    password="test_password",
                ),
                first_name="gaspar",
                surname="noriega",
                phone_number="3512421500",
                birthdate=date_now(),
                government_id="40123123",
                social_media_url=self.TEST_SOCIAL_MEDIA_URL,
            )
        )

        self.assertEqual(
            1,
            len(self.email_gateway.email_cache),
        )

        self.assertEqual(
            self.TEST_EMAIL,
            self.email_gateway.email_cache[0].recipient,
        )

        self.assertEqual(
            SocialEmailSubjects.VERIFY_ACCOUNT.value,
            self.email_gateway.email_cache[0].subject,
        )

        self.assertTrue(
            VerifyAccountUrls.VERIFY_PERSONAL_PROFILE.value
            in self.email_gateway.email_cache[0].body
        )

    async def test_create_org_admin_triggers_mail(self) -> None:
        await self.create_org_profile.execute(
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
                    social_media_url=self.TEST_SOCIAL_MEDIA_URL,
                ),
            )
        )

        self.assertEqual(
            1,
            len(self.email_gateway.email_cache),
        )

        self.assertEqual(
            self.TEST_EMAIL,
            self.email_gateway.email_cache[0].recipient,
        )

        self.assertEqual(
            SocialEmailSubjects.VERIFY_ACCOUNT.value,
            self.email_gateway.email_cache[0].subject,
        )

        self.assertTrue(
            VerifyAccountUrls.VERIFY_ORG_ADMIN.value
            in self.email_gateway.email_cache[0].body
        )

    async def test_resend_verification_request_triggers_mail_sent(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            profile_data = await self.create_profile(
                uow,
            )

        self.email_gateway.clear_cache()

        await self.resend_verification_request_use_case.execute(
            ResendVerificationRequest.Request(
                email=profile_data.email,
            )
        )

        self.assertEqual(
            1,
            len(self.email_gateway.email_cache),
        )

        self.assertEqual(
            profile_data.email,
            self.email_gateway.email_cache[0].recipient,
        )

        self.assertEqual(
            SocialEmailSubjects.VERIFY_ACCOUNT.value,
            self.email_gateway.email_cache[0].subject,
        )

    async def test_request_password_reset_triggers_mail(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            user = await self.create_profile(
                uow=uow,
            )

        self.email_gateway.clear_cache()

        await self.request_password_reset_use_case.execute(
            RequestPasswordResetUseCase.Request(
                email=user.email,
            )
        )

        self.assertEqual(
            1,
            len(self.email_gateway.email_cache),
        )

        self.assertEqual(
            user.email,
            self.email_gateway.email_cache[0].recipient,
        )

        self.assertEqual(
            SocialEmailSubjects.RESET_PASSWORD.value,
            self.email_gateway.email_cache[0].subject,
        )

    async def test_verify_organization_triggers_mail(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            user = await self.create_organizational_profile(
                uow=uow,
            )

            staff_user = await self.create_profile(uow=uow, email="STAFF_EMAIL")

        self.email_gateway.clear_cache()

        await self.verify_organization_use_case.execute(
            staff_user.account_id, user.organization.entity_id
        )

        self.assertEqual(
            1,
            len(self.email_gateway.email_cache),
        )

        self.assertEqual(
            user.profile_data.email,
            self.email_gateway.email_cache[0].recipient,
        )

        self.assertEqual(
            SocialEmailSubjects.ORGANIZATION_VERIFIED.value,
            self.email_gateway.email_cache[0].subject,
        )
