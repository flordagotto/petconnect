from bounded_contexts.adoptions_domain.enum import AdoptionApplicationStates
from bounded_contexts.adoptions_domain.services.adoption_applications_service import (
    ModifyAdoptionApplicationData,
)
from bounded_contexts.adoptions_domain.use_cases.edit_adoption_application import (
    EditAdoptionApplicationUseCase,
)
from bounded_contexts.pets_domain.exceptions import (
    PetNotFoundByAdoptionAnimalIdException,
)
from common.testing import BaseUseCaseTest
from common.testing.base_testing_utils import BaseTestingUtils
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work, make_unit_of_work


class TestEventAdoptedAnimal(BaseUseCaseTest, BaseTestingUtils):
    @unit_of_work
    async def initial_data(self, uow: UnitOfWork) -> None:
        self.adoption_giver_organizational_profile = (
            await self.create_organizational_profile(uow=uow)
        )
        self.adopter_profile = await self.create_profile(uow=uow)

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

        self.use_case: EditAdoptionApplicationUseCase = self.dependencies.resolve(
            EditAdoptionApplicationUseCase
        )

        await self.initial_data()

    async def test_event_animal_adopted_creates_pet(
        self,
    ) -> None:
        new_adoption_application_data = ModifyAdoptionApplicationData(
            entity_id=self.adoption_application_organizational_profile.adoption_application_data.entity_id,
            state=AdoptionApplicationStates.ACCEPTED,
        )
        await self.use_case.execute(
            EditAdoptionApplicationUseCase.Request(
                actor_account_id=self.adoption_giver_organizational_profile.profile_data.account_id,
                application_data=new_adoption_application_data,
            )
        )

        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            adopted_animal = self.animal_data_organizational_profile
            new_pet = await self.pet_service.get_pet_by_adoption_animal_id(
                uow=uow, adoption_animal_id=adopted_animal.entity_id
            )

            self.assertEqual(
                (
                    adopted_animal.animal_name,
                    adopted_animal.birth_year,
                    adopted_animal.species,
                    adopted_animal.gender,
                    adopted_animal.size,
                    adopted_animal.sterilized,
                    adopted_animal.vaccinated,
                    adopted_animal.picture,
                    False,
                    adopted_animal.race,
                    adopted_animal.special_care,
                    self.adopter_profile.profile_id,
                ),
                (
                    new_pet.animal_name,
                    new_pet.birth_year,
                    new_pet.species,
                    new_pet.gender,
                    new_pet.size,
                    new_pet.sterilized,
                    new_pet.vaccinated,
                    new_pet.picture,
                    new_pet.lost,
                    new_pet.race,
                    new_pet.special_care,
                    new_pet.profile_id,
                ),
            )

    async def test_application_rejected_does_not_raise_event(
        self,
    ) -> None:
        new_adoption_application_data = ModifyAdoptionApplicationData(
            entity_id=self.adoption_application_organizational_profile.adoption_application_data.entity_id,
            state=AdoptionApplicationStates.REJECTED,
        )
        await self.use_case.execute(
            EditAdoptionApplicationUseCase.Request(
                actor_account_id=self.adoption_giver_organizational_profile.profile_data.account_id,
                application_data=new_adoption_application_data,
            )
        )

        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            adopted_animal = self.animal_data_organizational_profile

            with self.assertRaises(PetNotFoundByAdoptionAnimalIdException):
                await self.pet_service.get_pet_by_adoption_animal_id(
                    uow=uow, adoption_animal_id=adopted_animal.entity_id
                )
