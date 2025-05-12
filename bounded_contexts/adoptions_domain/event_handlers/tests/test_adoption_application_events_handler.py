from bounded_contexts.adoptions_domain.email import AdoptionEmailSubjects
from bounded_contexts.adoptions_domain.enum import AdoptionApplicationStates
from bounded_contexts.adoptions_domain.services.adoption_applications_service import (
    ModifyAdoptionApplicationData,
)
from bounded_contexts.adoptions_domain.use_cases.edit_adoption_application import (
    EditAdoptionApplicationUseCase,
)
from common.testing import BaseUseCaseTest
from common.testing.base_testing_utils import BaseTestingUtils
from infrastructure.email import BaseEmailGateway
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class TestAdoptionApplicationEventHandler(BaseUseCaseTest, BaseTestingUtils):
    @unit_of_work
    async def initial_data(self, uow: UnitOfWork) -> None:
        self.adoption_giver_personal_profile = await self.create_profile(uow=uow)

        self.adoption_giver_organizational_profile = (
            await self.create_organizational_profile(uow=uow)
        )

        self.adopter_profile = await self.create_profile(uow=uow)

        self.animal_data_personal_profile = (
            await self.create_adoption_animal(
                uow=uow, actor_profile=self.adoption_giver_personal_profile
            )
        ).adoption_animal_data

        self.adoption_application_personal_profile = (
            await self.create_adoption_application(
                uow=uow,
                actor_profile=self.adopter_profile,
                animal_id=self.animal_data_personal_profile.entity_id,
            )
        )

        self.animal_data_organizational_profile = (
            await self.create_adoption_animal(
                uow=uow,
                actor_profile=self.adoption_giver_organizational_profile.profile_data,
            )
        ).adoption_animal_data

        self.adoption_application_organizational_profile = (
            await self.create_adoption_application(
                uow=uow,
                actor_profile=self.adopter_profile,
                animal_id=self.animal_data_organizational_profile.entity_id,
            )
        )

    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.edit_adoption_application_use_case: EditAdoptionApplicationUseCase = (
            self.dependencies.resolve(EditAdoptionApplicationUseCase)
        )

        self.email_gateway: BaseEmailGateway = self.dependencies.resolve(
            BaseEmailGateway
        )

        self.email_gateway.clear_cache()

        await self.initial_data()

    async def test_approve_adoption_application_triggers_mail_sent(self) -> None:
        await self.edit_adoption_application_use_case.execute(
            EditAdoptionApplicationUseCase.Request(
                actor_account_id=self.adoption_giver_personal_profile.account_id,
                application_data=ModifyAdoptionApplicationData(
                    entity_id=self.adoption_application_personal_profile.adoption_application_data.entity_id,
                    state=AdoptionApplicationStates.ACCEPTED,
                ),
            )
        )

        application_emails = [
            email
            for email in self.email_gateway.email_cache
            if email.subject
            == AdoptionEmailSubjects.ADOPTION_APPLICATION_STATUS_UPDATED.value
        ]

        self.assertEqual(
            1,
            len(application_emails),
        )

        self.assertEqual(
            self.adopter_profile.email,
            application_emails[0].recipient,
        )

        self.assertTrue("fue aceptada" in application_emails[0].body)

    async def test_reject_adoption_application_triggers_mail_sent(self) -> None:
        await self.edit_adoption_application_use_case.execute(
            EditAdoptionApplicationUseCase.Request(
                actor_account_id=self.adoption_giver_organizational_profile.profile_data.account_id,
                application_data=ModifyAdoptionApplicationData(
                    entity_id=self.adoption_application_organizational_profile.adoption_application_data.entity_id,
                    state=AdoptionApplicationStates.REJECTED,
                ),
            )
        )

        application_emails = [
            email
            for email in self.email_gateway.email_cache
            if email.subject
            == AdoptionEmailSubjects.ADOPTION_APPLICATION_STATUS_UPDATED.value
        ]

        self.assertEqual(
            1,
            len(application_emails),
        )

        self.assertEqual(
            self.adopter_profile.email,
            application_emails[0].recipient,
        )

        self.assertTrue("fue rechazada" in application_emails[0].body)
