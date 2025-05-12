from bounded_contexts.adoptions_domain.enum import AdoptionAnimalStates
from bounded_contexts.adoptions_domain.exceptions import (
    AnimalNotFoundByIdException,
    AdoptionAnimalUnauthorizedAccessException,
)
from bounded_contexts.adoptions_domain.services.adoptions_animals_service import (
    AdoptionAnimalData,
)
from bounded_contexts.adoptions_domain.use_cases import DeleteAdoptionAnimalUseCase
from bounded_contexts.social_domain.entities import (
    AnimalSpecies,
    AnimalGender,
    AnimalSize,
)
from bounded_contexts.pets_domain.use_cases import DeletePetUseCase
from common.testing import BaseUseCaseTest
from common.testing.base_testing_utils import BaseTestingUtils
from infrastructure.uow_abstraction import make_unit_of_work, UnitOfWork, unit_of_work


class TestDeleteAdoptionAnimal(BaseUseCaseTest, BaseTestingUtils):
    @unit_of_work
    async def initial_data(self, uow: UnitOfWork) -> None:
        self.profile1 = await self.create_profile(uow=uow)
        self.profile2 = await self.create_profile(uow=uow)

        animal_data1 = AdoptionAnimalData(
            entity_id="",
            animal_name="Pepito",
            birth_year=2023,
            species=AnimalSpecies.CAT,
            gender=AnimalGender.MALE,
            size=AnimalSize.BIG,
            sterilized=True,
            vaccinated=True,
            picture="https://.../picture/id_pepito",
            state=AdoptionAnimalStates.FOR_ADOPTION,
            race="siames",
            special_care="medicacion",
        )

        animal_data2 = AdoptionAnimalData(
            entity_id="",
            animal_name="Tale",
            birth_year=2023,
            species=AnimalSpecies.CAT,
            gender=AnimalGender.MALE,
            size=AnimalSize.SMALL,
            sterilized=True,
            vaccinated=False,
            picture="https://.../picture/id_tale",
            state=AdoptionAnimalStates.FOR_ADOPTION,
            race=None,
            special_care="",
            description="gatito muy lindo",
        )

        animal_data3 = AdoptionAnimalData(
            entity_id="",
            animal_name="Felipe",
            birth_year=2023,
            species=AnimalSpecies.DOG,
            gender=AnimalGender.MALE,
            size=AnimalSize.SMALL,
            sterilized=False,
            vaccinated=True,
            picture="https://.../picture/id_felipe",
            state=AdoptionAnimalStates.FOR_ADOPTION,
            race=None,
            special_care="",
        )

        self.adoption_animal1 = await self.create_adoption_animal(
            uow=uow, actor_profile=self.profile1, adoption_animal_data=animal_data1
        )
        self.adoption_animal2 = await self.create_adoption_animal(
            uow=uow, actor_profile=self.profile1, adoption_animal_data=animal_data2
        )
        self.adoption_animal3 = await self.create_adoption_animal(
            uow=uow, actor_profile=self.profile2, adoption_animal_data=animal_data3
        )

    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.use_case: DeleteAdoptionAnimalUseCase = self.dependencies.resolve(
            DeleteAdoptionAnimalUseCase
        )

        await self.initial_data()

    async def test_delete_adoption_animal_success(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            animal_data: AdoptionAnimalData = await self.get_all_adoption_animal(
                uow=uow,
                adoption_animal_id=self.adoption_animal1.adoption_animal_data.entity_id,
            )

        await self.use_case.execute(
            DeletePetUseCase.Request(
                entity_id=animal_data.entity_id,
                actor_account_id=self.profile1.account_id,
            )
        )

        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            deleted_animal_data: AdoptionAnimalData = await self.get_all_adoption_animal(
                uow=uow,
                adoption_animal_id=self.adoption_animal1.adoption_animal_data.entity_id,
            )

            self.assertTrue(deleted_animal_data.deleted)

    async def test_delete_adoption_animal_fails(self) -> None:
        with self.assertRaises(AnimalNotFoundByIdException):
            await self.use_case.execute(
                DeletePetUseCase.Request(
                    entity_id="12345", actor_account_id=self.profile1.account_id
                )
            )

    async def test_delete_foreign_adoption_animal_fails(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            animal_data: AdoptionAnimalData = await self.get_all_adoption_animal(
                uow=uow,
                adoption_animal_id=self.adoption_animal1.adoption_animal_data.entity_id,
            )

        with self.assertRaises(AdoptionAnimalUnauthorizedAccessException):
            await self.use_case.execute(
                DeletePetUseCase.Request(
                    entity_id=animal_data.entity_id,
                    actor_account_id=self.profile2.account_id,
                )
            )

    # TODO: tests for events (deleted animal -> reject applications) are missing
