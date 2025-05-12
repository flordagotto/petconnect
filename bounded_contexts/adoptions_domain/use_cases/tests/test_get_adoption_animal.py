from bounded_contexts.adoptions_domain.entities import AdoptionAnimal
from bounded_contexts.adoptions_domain.exceptions import AnimalNotFoundByIdException
from bounded_contexts.adoptions_domain.use_cases import GetAdoptionAnimalUseCase
from common.testing import BaseUseCaseTest
from common.testing.base_testing_utils import BaseTestingUtils
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work, make_unit_of_work


class TestGetAdoptionAnimal(BaseUseCaseTest, BaseTestingUtils):
    TEST_ADOPTION_ANIMAL_ID: str = "12345"

    @unit_of_work
    async def initial_data(self, uow: UnitOfWork) -> None:
        self.profile = await self.create_profile(uow=uow)
        self.animal_data = (
            await self.create_adoption_animal(uow=uow, actor_profile=self.profile)
        ).adoption_animal_data

    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.use_case: GetAdoptionAnimalUseCase = self.dependencies.resolve(
            GetAdoptionAnimalUseCase
        )

        await self.initial_data()

    async def test_get_adoption_animal_success(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            adoption_animal: AdoptionAnimal = (
                await self.adoption_animal_service.get_adoption_animal_by_id(
                    uow=uow, entity_id=self.animal_data.entity_id
                )
            )

        self.assertEqual(
            (
                adoption_animal.entity_id,
                adoption_animal.animal_name,
                adoption_animal.birth_year,
                adoption_animal.species,
                adoption_animal.gender,
                adoption_animal.size,
                adoption_animal.sterilized,
                adoption_animal.vaccinated,
                adoption_animal.picture,
                adoption_animal.state,
                adoption_animal.race,
                adoption_animal.special_care,
                adoption_animal.description,
                adoption_animal.publication_date,
            ),
            (
                self.animal_data.entity_id,
                self.animal_data.animal_name,
                self.animal_data.birth_year,
                self.animal_data.species,
                self.animal_data.gender,
                self.animal_data.size,
                self.animal_data.sterilized,
                self.animal_data.vaccinated,
                self.animal_data.picture,
                self.animal_data.state,
                self.animal_data.race,
                self.animal_data.special_care,
                self.animal_data.description,
                self.animal_data.publication_date,
            ),
        )

    async def test_get_pet_fails(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            with self.assertRaises(AnimalNotFoundByIdException):
                await self.adoption_animal_service.get_adoption_animal_by_id(
                    uow=uow, entity_id=self.TEST_ADOPTION_ANIMAL_ID
                )
