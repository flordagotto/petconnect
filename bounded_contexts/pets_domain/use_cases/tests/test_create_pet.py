from bounded_contexts.pets_domain.entities import Pet
from bounded_contexts.social_domain.entities.animal import (
    AnimalSpecies,
    AnimalGender,
    AnimalSize,
)
from bounded_contexts.pets_domain.exceptions.owner_is_not_a_personal_profile_exception import (
    OwnerIsNotAPersonalProfileException,
)
from bounded_contexts.pets_domain.use_cases import CreatePetUseCase
from bounded_contexts.pets_domain.views import PetView
from common.testing import BaseUseCaseTest
from common.testing.base_testing_utils import (
    BaseTestingUtils,
    ProfileData,
    OrganizationalProfileData,
)
from infrastructure.uow_abstraction import make_unit_of_work


class TestCreatePet(BaseUseCaseTest, BaseTestingUtils):
    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.use_case: CreatePetUseCase = self.dependencies.resolve(CreatePetUseCase)

    async def test_create_pet_success(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            profile: ProfileData = await self.create_profile(uow=uow)

        view: PetView = await self.use_case.execute(
            CreatePetUseCase.Request(
                actor_account_id=profile.account_id,
                animal_name="new pet name hehe",
                lost=True,
                birth_year=2005,
                species=AnimalSpecies.CAT,
                gender=AnimalGender.FEMALE,
                size=AnimalSize.MEDIUM,
                sterilized=False,
                vaccinated=True,
                picture="https://petconnect.icu/picture/id_pepito_2.jpg",
            )
        )

        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            pet: Pet = await self.pet_service.get_pet_by_id(
                uow=uow, entity_id=view.entity_id
            )

            self.assertEqual(
                (
                    pet.entity_id,
                    pet.animal_name,
                    pet.lost,
                    pet.birth_year,
                    pet.species,
                    pet.gender,
                    pet.size,
                    pet.sterilized,
                    pet.vaccinated,
                    pet.picture,
                ),
                (
                    view.entity_id,
                    view.animal_name,
                    view.lost,
                    view.birth_year,
                    view.species,
                    view.gender,
                    view.size,
                    view.sterilized,
                    view.vaccinated,
                    view.picture,
                ),
            )

    async def test_create_pet_fail(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            profile: OrganizationalProfileData = (
                await self.create_organizational_profile(uow=uow)
            )

        with self.assertRaises(OwnerIsNotAPersonalProfileException):
            await self.use_case.execute(
                CreatePetUseCase.Request(
                    actor_account_id=profile.profile_data.account_id,
                    animal_name="new pet name hehe",
                    lost=True,
                    birth_year=2005,
                    species=AnimalSpecies.CAT,
                    gender=AnimalGender.FEMALE,
                    size=AnimalSize.MEDIUM,
                    sterilized=False,
                    vaccinated=True,
                    picture="https://petconnect.icu/picture/id_pepito_2.jpg",
                )
            )
