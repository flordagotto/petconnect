from bounded_contexts.adoptions_domain.enum import AdoptionAnimalStates
from bounded_contexts.adoptions_domain.services.adoptions_animals_service import (
    AdoptionAnimalData,
)
from bounded_contexts.adoptions_domain.use_cases.get_adoption_animals import (
    GetAdoptionAnimalsUseCase,
)
from bounded_contexts.adoptions_domain.views import AdoptionAnimalListView
from bounded_contexts.social_domain.entities.animal import (
    AnimalSpecies,
    AnimalGender,
    AnimalSize,
)
from common.testing import BaseUseCaseTest
from common.testing.base_testing_utils import (
    BaseTestingUtils,
    AdoptionAnimalDataForTesting,
)
from infrastructure.uow_abstraction import unit_of_work, UnitOfWork


class TestGetPetsUseCase(BaseUseCaseTest, BaseTestingUtils):
    TEST_NO_LIMIT = None
    TEST_OFFSET_ZERO = 0
    TEST_LIMIT = 2
    TEST_OFFSET = 1

    @unit_of_work
    async def initial_data(self, uow: UnitOfWork) -> None:
        self.profile1 = await self.create_profile(uow=uow)
        self.profile2 = await self.create_profile(uow=uow)
        self.organizational_profile1 = await self.create_organizational_profile(uow=uow)
        self.organizational_profile2 = (
            await self.create_organizational_collaborator_profile(
                uow=uow,
                organization_id=self.organizational_profile1.organization.entity_id,
                account_email="collaborator@gmail.com",
            )
        )

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

        animal_data4 = AdoptionAnimalData(
            entity_id="",
            animal_name="Lola",
            birth_year=2023,
            species=AnimalSpecies.DOG,
            gender=AnimalGender.FEMALE,
            size=AnimalSize.MEDIUM,
            sterilized=False,
            vaccinated=False,
            picture="https://.../picture/id_lola",
            state=AdoptionAnimalStates.FOR_ADOPTION,
            race=None,
            special_care="",
        )

        animal_data5 = AdoptionAnimalData(
            entity_id="",
            animal_name="Luli",
            birth_year=2023,
            species=AnimalSpecies.DOG,
            gender=AnimalGender.FEMALE,
            size=AnimalSize.MEDIUM,
            sterilized=False,
            vaccinated=False,
            picture="https://.../picture/id_luli",
            state=AdoptionAnimalStates.FOR_ADOPTION,
            race=None,
            special_care="",
        )

        animal_data6 = AdoptionAnimalData(
            entity_id="",
            animal_name="Michi",
            birth_year=2023,
            species=AnimalSpecies.CAT,
            gender=AnimalGender.FEMALE,
            size=AnimalSize.MEDIUM,
            sterilized=False,
            vaccinated=False,
            picture="https://.../picture/id_michi",
            state=AdoptionAnimalStates.FOR_ADOPTION,
            race=None,
            special_care="",
        )

        adoption_animal1 = await self.create_adoption_animal(
            uow=uow, actor_profile=self.profile1, adoption_animal_data=animal_data1
        )
        adoption_animal2 = await self.create_adoption_animal(
            uow=uow, actor_profile=self.profile1, adoption_animal_data=animal_data2
        )
        adoption_animal3 = await self.create_adoption_animal(
            uow=uow, actor_profile=self.profile2, adoption_animal_data=animal_data3
        )
        adoption_animal4 = await self.create_adoption_animal(
            uow=uow, actor_profile=self.profile2, adoption_animal_data=animal_data4
        )
        adoption_animal5 = await self.create_adoption_animal(
            uow=uow,
            actor_profile=self.organizational_profile1.profile_data,
            adoption_animal_data=animal_data5,
        )
        adoption_animal6 = await self.create_adoption_animal(
            uow=uow,
            actor_profile=self.organizational_profile2.profile_data,
            adoption_animal_data=animal_data6,
        )

        animals_not_ordered: list[AdoptionAnimalDataForTesting] = [
            adoption_animal1,
            adoption_animal2,
            adoption_animal3,
            adoption_animal4,
            adoption_animal5,
            adoption_animal6,
        ]
        self.animals = sorted(
            animals_not_ordered,
            key=lambda animal: animal.adoption_animal_data.animal_name,
        )

    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.use_case: GetAdoptionAnimalsUseCase = self.dependencies.resolve(
            GetAdoptionAnimalsUseCase
        )

        await self.initial_data()

    async def test_get_adoption_animals_all_species_success(self) -> None:
        list_view: AdoptionAnimalListView = await self.use_case.execute(
            GetAdoptionAnimalsUseCase.Request(
                limit=self.TEST_NO_LIMIT,
                offset=self.TEST_OFFSET_ZERO,
                account_id=None,
                species=[],
            )
        )

        self.assertEqual(len(self.animals), list_view.total_count)

        for i in range(len(list_view.items)):
            animal_data = self.animals[i].adoption_animal_data
            self.assertEqual(
                (
                    animal_data.entity_id,
                    animal_data.animal_name,
                    animal_data.birth_year,
                    animal_data.species,
                    animal_data.gender,
                    animal_data.size,
                    animal_data.sterilized,
                    animal_data.vaccinated,
                    animal_data.picture,
                    animal_data.state,
                    animal_data.race,
                    animal_data.special_care,
                    animal_data.description,
                    animal_data.deleted,
                    animal_data.publication_date,
                ),
                (
                    list_view.items[i].entity_id,
                    list_view.items[i].animal_name,
                    list_view.items[i].birth_year,
                    list_view.items[i].species,
                    list_view.items[i].gender,
                    list_view.items[i].size,
                    list_view.items[i].sterilized,
                    list_view.items[i].vaccinated,
                    list_view.items[i].picture,
                    list_view.items[i].state,
                    list_view.items[i].race,
                    list_view.items[i].special_care,
                    list_view.items[i].description,
                    list_view.items[i].deleted,
                    list_view.items[i].publication_date,
                ),
            )

    async def test_get_adoption_animals_all_species_from_owner(self) -> None:
        list_view: AdoptionAnimalListView = await self.use_case.execute(
            GetAdoptionAnimalsUseCase.Request(
                limit=None,
                offset=self.TEST_OFFSET_ZERO,
                account_id=self.profile1.account_id,
                species=[],
            )
        )

        dogs_from_owner = [
            animal.adoption_animal_data
            for animal in self.animals
            if animal.profile_id == self.profile1.profile_id
        ]

        self.assertEqual(len(dogs_from_owner), list_view.total_count)

        for i in range(len(list_view.items)):
            self.assertEqual(
                (
                    dogs_from_owner[i].entity_id,
                    dogs_from_owner[i].animal_name,
                    dogs_from_owner[i].birth_year,
                    dogs_from_owner[i].species,
                    dogs_from_owner[i].gender,
                    dogs_from_owner[i].size,
                    dogs_from_owner[i].sterilized,
                    dogs_from_owner[i].vaccinated,
                    dogs_from_owner[i].picture,
                    dogs_from_owner[i].state,
                    dogs_from_owner[i].race,
                    dogs_from_owner[i].special_care,
                    dogs_from_owner[i].description,
                    dogs_from_owner[i].deleted,
                    dogs_from_owner[i].publication_date,
                ),
                (
                    list_view.items[i].entity_id,
                    list_view.items[i].animal_name,
                    list_view.items[i].birth_year,
                    list_view.items[i].species,
                    list_view.items[i].gender,
                    list_view.items[i].size,
                    list_view.items[i].sterilized,
                    list_view.items[i].vaccinated,
                    list_view.items[i].picture,
                    list_view.items[i].state,
                    list_view.items[i].race,
                    list_view.items[i].special_care,
                    list_view.items[i].description,
                    list_view.items[i].deleted,
                    list_view.items[i].publication_date,
                ),
            )

    async def test_get_adoption_animals_pagination_with_limit(self) -> None:
        list_view: AdoptionAnimalListView = await self.use_case.execute(
            GetAdoptionAnimalsUseCase.Request(
                limit=self.TEST_LIMIT,
                offset=self.TEST_OFFSET_ZERO,
                account_id=None,
                species=[],
            )
        )

        self.assertEqual(len(self.animals), list_view.total_count)
        self.assertEqual(self.TEST_LIMIT, len(list_view.items))

        for i in range(self.TEST_LIMIT):
            animal_data = self.animals[i].adoption_animal_data
            self.assertEqual(
                (
                    animal_data.entity_id,
                    animal_data.animal_name,
                    animal_data.birth_year,
                    animal_data.species,
                    animal_data.gender,
                    animal_data.size,
                    animal_data.sterilized,
                    animal_data.vaccinated,
                    animal_data.picture,
                    animal_data.state,
                    animal_data.race,
                    animal_data.special_care,
                    animal_data.description,
                    animal_data.deleted,
                    animal_data.publication_date,
                ),
                (
                    list_view.items[i].entity_id,
                    list_view.items[i].animal_name,
                    list_view.items[i].birth_year,
                    list_view.items[i].species,
                    list_view.items[i].gender,
                    list_view.items[i].size,
                    list_view.items[i].sterilized,
                    list_view.items[i].vaccinated,
                    list_view.items[i].picture,
                    list_view.items[i].state,
                    list_view.items[i].race,
                    list_view.items[i].special_care,
                    list_view.items[i].description,
                    list_view.items[i].deleted,
                    list_view.items[i].publication_date,
                ),
            )

    async def test_get_adoption_animals_pagination_with_offset(self) -> None:
        list_view: AdoptionAnimalListView = await self.use_case.execute(
            GetAdoptionAnimalsUseCase.Request(
                limit=None, offset=self.TEST_OFFSET, account_id=None, species=[]
            )
        )

        self.assertEqual(len(self.animals), list_view.total_count)
        index_offset = self.TEST_OFFSET

        for animal in list_view.items:
            animal_data = self.animals[index_offset].adoption_animal_data
            self.assertEqual(
                (
                    animal_data.entity_id,
                    animal_data.animal_name,
                    animal_data.birth_year,
                    animal_data.species,
                    animal_data.gender,
                    animal_data.size,
                    animal_data.sterilized,
                    animal_data.vaccinated,
                    animal_data.picture,
                    animal_data.state,
                    animal_data.race,
                    animal_data.special_care,
                    animal_data.description,
                    animal_data.deleted,
                    animal_data.publication_date,
                ),
                (
                    animal.entity_id,
                    animal.animal_name,
                    animal.birth_year,
                    animal.species,
                    animal.gender,
                    animal.size,
                    animal.sterilized,
                    animal.vaccinated,
                    animal.picture,
                    animal.state,
                    animal.race,
                    animal.special_care,
                    animal.description,
                    animal.deleted,
                    animal.publication_date,
                ),
            )
            index_offset += 1

    async def test_get_adoption_animals_filter_by_species(self) -> None:
        species: list[AnimalSpecies] = [AnimalSpecies.DOG]
        list_view: AdoptionAnimalListView = await self.use_case.execute(
            GetAdoptionAnimalsUseCase.Request(
                limit=None,
                offset=self.TEST_OFFSET_ZERO,
                account_id=None,
                species=species,
            )
        )

        dogs = [
            animal.adoption_animal_data
            for animal in self.animals
            if animal.adoption_animal_data.species in species
        ]
        self.assertEqual(len(dogs), list_view.total_count)

        for i in range(len(list_view.items)):
            self.assertEqual(
                (
                    dogs[i].entity_id,
                    dogs[i].animal_name,
                    dogs[i].birth_year,
                    dogs[i].species,
                    dogs[i].gender,
                    dogs[i].size,
                    dogs[i].sterilized,
                    dogs[i].vaccinated,
                    dogs[i].picture,
                    dogs[i].state,
                    dogs[i].race,
                    dogs[i].special_care,
                    dogs[i].description,
                    dogs[i].deleted,
                    dogs[i].publication_date,
                ),
                (
                    list_view.items[i].entity_id,
                    list_view.items[i].animal_name,
                    list_view.items[i].birth_year,
                    list_view.items[i].species,
                    list_view.items[i].gender,
                    list_view.items[i].size,
                    list_view.items[i].sterilized,
                    list_view.items[i].vaccinated,
                    list_view.items[i].picture,
                    list_view.items[i].state,
                    list_view.items[i].race,
                    list_view.items[i].special_care,
                    list_view.items[i].description,
                    list_view.items[i].deleted,
                    list_view.items[i].publication_date,
                ),
            )

    async def test_get_adoption_animals_filter_by_species_from_owner(self) -> None:
        species: list[AnimalSpecies] = [AnimalSpecies.DOG]
        list_view: AdoptionAnimalListView = await self.use_case.execute(
            GetAdoptionAnimalsUseCase.Request(
                limit=None,
                offset=self.TEST_OFFSET_ZERO,
                account_id=self.profile2.account_id,
                species=species,
            )
        )

        dogs_from_owner = [
            animal.adoption_animal_data
            for animal in self.animals
            if animal.adoption_animal_data.species in species
            and animal.profile_id == self.profile2.profile_id
        ]

        self.assertEqual(len(dogs_from_owner), list_view.total_count)

        for i in range(len(list_view.items)):
            self.assertEqual(
                (
                    dogs_from_owner[i].entity_id,
                    dogs_from_owner[i].animal_name,
                    dogs_from_owner[i].birth_year,
                    dogs_from_owner[i].species,
                    dogs_from_owner[i].gender,
                    dogs_from_owner[i].size,
                    dogs_from_owner[i].sterilized,
                    dogs_from_owner[i].vaccinated,
                    dogs_from_owner[i].picture,
                    dogs_from_owner[i].state,
                    dogs_from_owner[i].race,
                    dogs_from_owner[i].special_care,
                    dogs_from_owner[i].description,
                    dogs_from_owner[i].deleted,
                    dogs_from_owner[i].publication_date,
                ),
                (
                    list_view.items[i].entity_id,
                    list_view.items[i].animal_name,
                    list_view.items[i].birth_year,
                    list_view.items[i].species,
                    list_view.items[i].gender,
                    list_view.items[i].size,
                    list_view.items[i].sterilized,
                    list_view.items[i].vaccinated,
                    list_view.items[i].picture,
                    list_view.items[i].state,
                    list_view.items[i].race,
                    list_view.items[i].special_care,
                    list_view.items[i].description,
                    list_view.items[i].deleted,
                    list_view.items[i].publication_date,
                ),
            )

    async def test_get_adoption_animals_from_organization(self) -> None:
        list_view: AdoptionAnimalListView = await self.use_case.execute(
            GetAdoptionAnimalsUseCase.Request(
                limit=None,
                offset=self.TEST_OFFSET_ZERO,
                account_id=self.organizational_profile1.profile_data.account_id,
                species=[],
            )
        )

        profile_ids_from_organization = [
            self.organizational_profile1.profile_data.profile_id,
            self.organizational_profile2.profile_data.profile_id,
        ]

        animals_from_organization = [
            animal.adoption_animal_data
            for animal in self.animals
            if animal.profile_id in profile_ids_from_organization
        ]

        self.assertEqual(len(animals_from_organization), list_view.total_count)

        for i in range(len(list_view.items)):
            self.assertEqual(
                (
                    animals_from_organization[i].entity_id,
                    animals_from_organization[i].animal_name,
                    animals_from_organization[i].birth_year,
                    animals_from_organization[i].species,
                    animals_from_organization[i].gender,
                    animals_from_organization[i].size,
                    animals_from_organization[i].sterilized,
                    animals_from_organization[i].vaccinated,
                    animals_from_organization[i].picture,
                    animals_from_organization[i].state,
                    animals_from_organization[i].race,
                    animals_from_organization[i].special_care,
                    animals_from_organization[i].description,
                    animals_from_organization[i].deleted,
                    animals_from_organization[i].publication_date,
                ),
                (
                    list_view.items[i].entity_id,
                    list_view.items[i].animal_name,
                    list_view.items[i].birth_year,
                    list_view.items[i].species,
                    list_view.items[i].gender,
                    list_view.items[i].size,
                    list_view.items[i].sterilized,
                    list_view.items[i].vaccinated,
                    list_view.items[i].picture,
                    list_view.items[i].state,
                    list_view.items[i].race,
                    list_view.items[i].special_care,
                    list_view.items[i].description,
                    list_view.items[i].deleted,
                    list_view.items[i].publication_date,
                ),
            )

    async def test_get_adoption_animals_filter_by_species_from_organization(
        self,
    ) -> None:
        species: list[AnimalSpecies] = [AnimalSpecies.DOG]
        list_view: AdoptionAnimalListView = await self.use_case.execute(
            GetAdoptionAnimalsUseCase.Request(
                limit=None,
                offset=self.TEST_OFFSET_ZERO,
                account_id=self.organizational_profile2.profile_data.account_id,
                species=species,
            )
        )

        profile_ids_from_organization = [
            self.organizational_profile1.profile_data.profile_id,
            self.organizational_profile2.profile_data.profile_id,
        ]

        dogs_from_owner = [
            animal.adoption_animal_data
            for animal in self.animals
            if animal.adoption_animal_data.species in species
            and animal.profile_id in profile_ids_from_organization
        ]

        self.assertEqual(len(dogs_from_owner), list_view.total_count)

        for i in range(len(list_view.items)):
            self.assertEqual(
                (
                    dogs_from_owner[i].entity_id,
                    dogs_from_owner[i].animal_name,
                    dogs_from_owner[i].birth_year,
                    dogs_from_owner[i].species,
                    dogs_from_owner[i].gender,
                    dogs_from_owner[i].size,
                    dogs_from_owner[i].sterilized,
                    dogs_from_owner[i].vaccinated,
                    dogs_from_owner[i].picture,
                    dogs_from_owner[i].state,
                    dogs_from_owner[i].race,
                    dogs_from_owner[i].special_care,
                    dogs_from_owner[i].description,
                    dogs_from_owner[i].deleted,
                    dogs_from_owner[i].publication_date,
                ),
                (
                    list_view.items[i].entity_id,
                    list_view.items[i].animal_name,
                    list_view.items[i].birth_year,
                    list_view.items[i].species,
                    list_view.items[i].gender,
                    list_view.items[i].size,
                    list_view.items[i].sterilized,
                    list_view.items[i].vaccinated,
                    list_view.items[i].picture,
                    list_view.items[i].state,
                    list_view.items[i].race,
                    list_view.items[i].special_care,
                    list_view.items[i].description,
                    list_view.items[i].deleted,
                    list_view.items[i].publication_date,
                ),
            )
