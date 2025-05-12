from bounded_contexts.adoptions_domain.entities import AdoptionApplication
from bounded_contexts.adoptions_domain.enum import (
    HousingTypes,
    OpenSpacesTypes,
    AdoptionAnimalStates,
)
from bounded_contexts.adoptions_domain.exceptions import (
    AdoptionApplicationForOwnAnimalException,
    ApplicationByOrganizationNotValidException,
    AnimalAlreadyAdoptedException,
    ProfileAlreadyAppliedException,
)
from bounded_contexts.adoptions_domain.services.adoptions_animals_service import (
    AdoptionAnimalData,
)
from bounded_contexts.adoptions_domain.use_cases.create_adoption_application import (
    CreateAdoptionApplicationUseCase,
)
from bounded_contexts.adoptions_domain.views import AdoptionApplicationView
from bounded_contexts.social_domain.entities import (
    AnimalSpecies,
    AnimalGender,
    AnimalSize,
)
from common.testing import BaseUseCaseTest
from common.testing.base_testing_utils import BaseTestingUtils, ProfileData
from infrastructure.uow_abstraction import make_unit_of_work, unit_of_work, UnitOfWork


class TestCreateAdoptionApplication(BaseUseCaseTest, BaseTestingUtils):
    @unit_of_work
    async def initial_data(self, uow: UnitOfWork) -> None:
        self.adoption_giver_profile = await self.create_profile(uow=uow)
        self.profile = await self.create_profile(uow=uow)
        self.organizational_profile = await self.create_organizational_profile(uow=uow)
        self.animal = (
            await self.create_adoption_animal(
                uow=uow, actor_profile=self.adoption_giver_profile
            )
        ).adoption_animal_data

        adopted_animal = AdoptionAnimalData(
            entity_id="",
            animal_name="Pepito",
            birth_year=2023,
            species=AnimalSpecies.OTHER,
            gender=AnimalGender.MALE,
            size=AnimalSize.BIG,
            sterilized=True,
            vaccinated=True,
            picture="https://.../picture/id_pepito",
            state=AdoptionAnimalStates.ADOPTED,
            race="siames",
            special_care="medicacion",
        )

        self.adopted_animal = (
            await self.create_adoption_animal(
                uow=uow,
                actor_profile=self.adoption_giver_profile,
                adoption_animal_data=adopted_animal,
            )
        ).adoption_animal_data

    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.use_case: CreateAdoptionApplicationUseCase = self.dependencies.resolve(
            CreateAdoptionApplicationUseCase
        )

        await self.initial_data()

    async def test_create_adoption_application_success(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            adopter_profile: ProfileData = await self.create_profile(uow=uow)

        view: AdoptionApplicationView = await self.use_case.execute(
            CreateAdoptionApplicationUseCase.Request(
                ever_had_pet=False,
                has_pet=True,
                type_of_housing=HousingTypes.HOUSE,
                open_space=OpenSpacesTypes.BALCONY,
                pet_time_commitment="tengo mucho tiempo",
                adoption_info="quiero una mascota",
                adopter_account_id=adopter_profile.account_id,
                animal_id=self.animal.entity_id,
                safety_in_open_spaces="tengo rejas en el balcon",
                animal_nice_to_others="es un gato amigable",
            )
        )

        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            application: AdoptionApplication = (
                await self.adoption_application_service.get_application_by_id(
                    uow=uow, entity_id=view.entity_id
                )
            )

            self.assertEqual(
                (
                    application.entity_id,
                    application.ever_had_pet,
                    application.has_pet,
                    application.type_of_housing,
                    application.pet_time_commitment,
                    application.adoption_info,
                    application.adopter_profile_id,
                    application.animal_id,
                    application.open_space,
                    application.safety_in_open_spaces,
                    application.animal_nice_to_others,
                    application.application_date,
                    application.state,
                ),
                (
                    view.entity_id,
                    view.ever_had_pet,
                    view.has_pet,
                    view.type_of_housing,
                    view.pet_time_commitment,
                    view.adoption_info,
                    view.adopter_profile_id,
                    view.animal_id,
                    view.open_space,
                    view.safety_in_open_spaces,
                    view.animal_nice_to_others,
                    view.application_date,
                    view.state,
                ),
            )

    async def test_create_adoption_application_from_organizational_profile_fails(
        self,
    ) -> None:
        with self.assertRaises(ApplicationByOrganizationNotValidException):
            await self.use_case.execute(
                CreateAdoptionApplicationUseCase.Request(
                    ever_had_pet=False,
                    has_pet=True,
                    type_of_housing=HousingTypes.HOUSE,
                    open_space=OpenSpacesTypes.BALCONY,
                    pet_time_commitment="tengo mucho tiempo",
                    adoption_info="quiero una mascota",
                    adopter_account_id=self.organizational_profile.profile_data.account_id,
                    animal_id=self.animal.entity_id,
                    safety_in_open_spaces="tengo rejas en el balcon",
                    animal_nice_to_others="es un gato amigable",
                )
            )

    async def test_create_adoption_application_for_own_animal_fails(self) -> None:
        with self.assertRaises(AdoptionApplicationForOwnAnimalException):
            await self.use_case.execute(
                CreateAdoptionApplicationUseCase.Request(
                    ever_had_pet=False,
                    has_pet=True,
                    type_of_housing=HousingTypes.HOUSE,
                    open_space=OpenSpacesTypes.BALCONY,
                    pet_time_commitment="tengo mucho tiempo",
                    adoption_info="quiero una mascota",
                    adopter_account_id=self.adoption_giver_profile.account_id,
                    animal_id=self.animal.entity_id,
                    safety_in_open_spaces="tengo rejas en el balcon",
                    animal_nice_to_others="es un gato amigable",
                )
            )

    async def test_create_adoption_application_for_already_adopted_animal_fails(
        self,
    ) -> None:
        with self.assertRaises(AnimalAlreadyAdoptedException):
            await self.use_case.execute(
                CreateAdoptionApplicationUseCase.Request(
                    ever_had_pet=False,
                    has_pet=True,
                    type_of_housing=HousingTypes.HOUSE,
                    open_space=OpenSpacesTypes.BALCONY,
                    pet_time_commitment="tengo mucho tiempo",
                    adoption_info="quiero una mascota",
                    adopter_account_id=self.profile.account_id,
                    animal_id=self.adopted_animal.entity_id,
                    safety_in_open_spaces="tengo rejas en el balcon",
                    animal_nice_to_others="es un gato amigable",
                )
            )

    async def test_create_adoption_application_from_profile_already_applied_fails(
        self,
    ) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            adopter_profile: ProfileData = await self.create_profile(uow=uow)

        await self.use_case.execute(
            CreateAdoptionApplicationUseCase.Request(
                ever_had_pet=False,
                has_pet=True,
                type_of_housing=HousingTypes.HOUSE,
                open_space=OpenSpacesTypes.BALCONY,
                pet_time_commitment="tengo mucho tiempo",
                adoption_info="quiero una mascota",
                adopter_account_id=adopter_profile.account_id,
                animal_id=self.animal.entity_id,
                safety_in_open_spaces="tengo rejas en el balcon",
                animal_nice_to_others="es un gato amigable",
            )
        )

        with self.assertRaises(ProfileAlreadyAppliedException):
            await self.use_case.execute(
                CreateAdoptionApplicationUseCase.Request(
                    ever_had_pet=False,
                    has_pet=True,
                    type_of_housing=HousingTypes.HOUSE,
                    open_space=OpenSpacesTypes.BALCONY,
                    pet_time_commitment="tengo mucho tiempo",
                    adoption_info="quiero una mascota",
                    adopter_account_id=adopter_profile.account_id,
                    animal_id=self.animal.entity_id,
                    safety_in_open_spaces="tengo rejas en el balcon",
                    animal_nice_to_others="es un gato amigable",
                )
            )
