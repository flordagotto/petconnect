from bounded_contexts.adoptions_domain.entities import AdoptionAnimal
from bounded_contexts.adoptions_domain.use_cases import CreateAdoptionAnimalUseCase
from bounded_contexts.adoptions_domain.views import AdoptionAnimalView
from bounded_contexts.social_domain.entities.animal import (
    AnimalSpecies,
    AnimalGender,
    AnimalSize,
)
from common.testing import BaseUseCaseTest
from common.testing.base_testing_utils import BaseTestingUtils, ProfileData
from infrastructure.uow_abstraction import make_unit_of_work


class TestCreateAdoptionAnimal(BaseUseCaseTest, BaseTestingUtils):
    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.use_case: CreateAdoptionAnimalUseCase = self.dependencies.resolve(
            CreateAdoptionAnimalUseCase
        )

    async def test_create_adoption_animal_success(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            profile: ProfileData = await self.create_profile(uow=uow)

        view: AdoptionAnimalView = await self.use_case.execute(
            CreateAdoptionAnimalUseCase.Request(
                account_id=profile.account_id,
                animal_name="flauta",
                birth_year=2005,
                species=AnimalSpecies.CAT,
                gender=AnimalGender.FEMALE,
                size=AnimalSize.MEDIUM,
                sterilized=False,
                vaccinated=True,
                picture="https://petconnect.icu/picture/id_flauta.jpg",
            )
        )

        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            adoption_animal: AdoptionAnimal = (
                await self.adoption_animal_service.get_adoption_animal_by_id(
                    uow=uow, entity_id=view.entity_id
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
                    adoption_animal.description,
                    adoption_animal.publication_date,
                ),
                (
                    view.entity_id,
                    view.animal_name,
                    view.birth_year,
                    view.species,
                    view.gender,
                    view.size,
                    view.sterilized,
                    view.vaccinated,
                    view.picture,
                    view.state,
                    view.description,
                    view.publication_date,
                ),
            )
