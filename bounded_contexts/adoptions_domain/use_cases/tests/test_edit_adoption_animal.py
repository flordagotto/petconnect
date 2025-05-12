from bounded_contexts.adoptions_domain.enum import AdoptionAnimalStates
from bounded_contexts.adoptions_domain.exceptions import (
    AdoptionAnimalUnauthorizedAccessException,
)
from bounded_contexts.adoptions_domain.services.adoptions_animals_service import (
    AdoptionAnimalData,
    ModifyAdoptionAnimalData,
)
from bounded_contexts.adoptions_domain.use_cases.edit_adoption_animal import (
    EditAdoptionAnimalUseCase,
)
from bounded_contexts.adoptions_domain.views import AdoptionAnimalView
from bounded_contexts.social_domain.entities import (
    AnimalSpecies,
    AnimalSize,
    AnimalGender,
)
from common.testing import BaseUseCaseTest
from common.testing.base_testing_utils import BaseTestingUtils
from infrastructure.uow_abstraction import make_unit_of_work, UnitOfWork, unit_of_work


class TestEditAdoptionAnimal(BaseUseCaseTest, BaseTestingUtils):
    @unit_of_work
    async def initial_data(self, uow: UnitOfWork) -> None:
        self.profile = await self.create_profile(uow=uow)
        self.animal_data = (
            await self.create_adoption_animal(uow=uow, actor_profile=self.profile)
        ).adoption_animal_data

    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.use_case: EditAdoptionAnimalUseCase = self.dependencies.resolve(
            EditAdoptionAnimalUseCase
        )

        await self.initial_data()

    async def test_edit_adoption_animal_success(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            animal_data: AdoptionAnimalData = await self.get_all_adoption_animal(
                uow=uow, adoption_animal_id=self.animal_data.entity_id
            )

            self.assertEqual(self.animal_data, animal_data)

        new_adoption_animal_data = ModifyAdoptionAnimalData(
            entity_id=self.animal_data.entity_id,
            animal_name="new pet name hehe",
            birth_year=2005,
            species=AnimalSpecies.CAT,
            gender=AnimalGender.FEMALE,
            size=AnimalSize.MEDIUM,
            sterilized=False,
            vaccinated=True,
            picture="https://petconnect.icu/picture/id_pepito_2.jpg",
            state=AdoptionAnimalStates.FOR_ADOPTION,
            description="new description",
        )

        view: AdoptionAnimalView = await self.use_case.execute(
            EditAdoptionAnimalUseCase.Request(
                actor_account_id=self.profile.account_id,
                animal_data=new_adoption_animal_data,
            )
        )

        self.assertEqual(
            new_adoption_animal_data,
            ModifyAdoptionAnimalData(
                entity_id=view.entity_id,
                animal_name=view.animal_name,
                birth_year=view.birth_year,
                species=view.species,
                gender=view.gender,
                size=view.size,
                sterilized=view.sterilized,
                vaccinated=view.vaccinated,
                picture=view.picture,
                state=view.state,
                description=view.description,
            ),
        )

        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            self.assertEqual(
                AdoptionAnimalData(
                    entity_id=view.entity_id,
                    animal_name=view.animal_name,
                    birth_year=view.birth_year,
                    species=view.species,
                    gender=view.gender,
                    size=view.size,
                    sterilized=view.sterilized,
                    vaccinated=view.vaccinated,
                    picture=view.picture,
                    state=view.state,
                    description=view.description,
                    publication_date=view.publication_date,
                ),
                await self.get_all_adoption_animal(
                    uow=uow, adoption_animal_id=self.animal_data.entity_id
                ),
            )

    async def test_edit_foreign_adoption_animal_fails(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            foreign_profile = await self.create_profile(uow=uow)

        new_adoption_animal_data = ModifyAdoptionAnimalData(
            entity_id=self.animal_data.entity_id,
            animal_name="new pet name hehe",
            birth_year=2002,
            species=AnimalSpecies.OTHER,
            gender=AnimalGender.FEMALE,
            size=AnimalSize.BIG,
            sterilized=False,
            vaccinated=False,
            picture="https://petconnect.icu/picture/id_pepito_3.jpg",
            state=AdoptionAnimalStates.FOR_ADOPTION,
        )

        with self.assertRaises(AdoptionAnimalUnauthorizedAccessException):
            await self.use_case.execute(
                EditAdoptionAnimalUseCase.Request(
                    actor_account_id=foreign_profile.account_id,
                    animal_data=new_adoption_animal_data,
                )
            )
