from bounded_contexts.pets_domain.email.pet_email_templates import PetEmailSubjects
from bounded_contexts.pets_domain.use_cases import RegisterPetSightUseCase
from common.testing import BaseUseCaseTest
from common.testing.base_testing_utils import BaseTestingUtils
from infrastructure.email import BaseEmailGateway
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class TestPetEventHandler(BaseUseCaseTest, BaseTestingUtils):
    TEST_LATITUDE: float = 35.70407437075822
    TEST_LONGITUDE: float = 139.5577317304603

    @unit_of_work
    async def initial_data(self, uow: UnitOfWork) -> None:
        self.profile = await self.create_profile(uow=uow)
        self.pet_data = (
            await self.create_pet(uow=uow, actor_profile=self.profile, lost=True)
        ).pet_data

    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.register_pet_sight: RegisterPetSightUseCase = self.dependencies.resolve(
            RegisterPetSightUseCase
        )

        self.email_gateway: BaseEmailGateway = self.dependencies.resolve(
            BaseEmailGateway
        )

        self.email_gateway.clear_cache()

        await self.initial_data()

    async def test_register_pet_sight_triggers_mail_sent(self) -> None:
        await self.register_pet_sight.execute(
            RegisterPetSightUseCase.Request(
                pet_id=self.pet_data.entity_id,
                latitude=self.TEST_LATITUDE,
                longitude=self.TEST_LONGITUDE,
                account_id=None,
            )
        )

        await self.register_pet_sight.execute(
            RegisterPetSightUseCase.Request(
                pet_id=self.pet_data.entity_id,
                latitude=self.TEST_LATITUDE,
                longitude=self.TEST_LONGITUDE,
                account_id=None,
            )
        )

        sight_emails = [
            email
            for email in self.email_gateway.email_cache
            if email.subject == PetEmailSubjects.PET_SIGHT.value
        ]

        self.assertEqual(
            1,
            len(sight_emails),
        )

        self.assertEqual(
            self.profile.email,
            sight_emails[0].recipient,
        )

        self.assertEqual(
            PetEmailSubjects.PET_SIGHT.value,
            sight_emails[0].subject,
        )

        self.assertTrue("lost-pets?petId=" in sight_emails[0].body)
