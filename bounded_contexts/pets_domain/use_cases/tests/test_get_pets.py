from bounded_contexts.social_domain.entities.animal import (
    AnimalSpecies,
    AnimalGender,
    AnimalSize,
)
from bounded_contexts.pets_domain.services import PetData, PetService
from bounded_contexts.pets_domain.use_cases import GetPetsUseCase
from bounded_contexts.pets_domain.views import PetListView
from common.testing import BaseUseCaseTest
from common.testing.base_testing_utils import BaseTestingUtils, PetDataForTesting
from infrastructure.uow_abstraction import unit_of_work, UnitOfWork, make_unit_of_work


class TestGetPetsUseCase(BaseUseCaseTest, BaseTestingUtils):
    TEST_NO_LIMIT = None
    TEST_OFFSET_ZERO = 0
    TEST_LIMIT = 2
    TEST_OFFSET = 1

    @unit_of_work
    async def initial_data(self, uow: UnitOfWork) -> None:
        self.profile1 = await self.create_profile(uow=uow)
        self.profile2 = await self.create_profile(uow=uow)

        pet_data1 = PetData(
            entity_id="",
            animal_name="Pepito",
            birth_year=2023,
            species=AnimalSpecies.OTHER,
            gender=AnimalGender.MALE,
            size=AnimalSize.BIG,
            sterilized=True,
            vaccinated=True,
            lost=False,
            qr_code="https://.../qr/id_pepito",
            picture="https://.../picture/id_pepito",
            race="siames",
            special_care="medicacion",
        )

        pet_data2 = PetData(
            entity_id="",
            animal_name="Tale",
            birth_year=2023,
            species=AnimalSpecies.CAT,
            gender=AnimalGender.MALE,
            size=AnimalSize.SMALL,
            sterilized=True,
            vaccinated=False,
            lost=False,
            qr_code="https://.../qr/id_pepito",
            picture="https://.../picture/id_pepito",
            race=None,
            special_care="",
        )

        pet_data3 = PetData(
            entity_id="",
            animal_name="Felipe",
            birth_year=2023,
            species=AnimalSpecies.DOG,
            gender=AnimalGender.MALE,
            size=AnimalSize.SMALL,
            sterilized=False,
            vaccinated=True,
            lost=True,
            qr_code="https://.../qr/id_pepito",
            picture="https://.../picture/id_pepito",
            race=None,
            special_care="",
        )

        pet_data4 = PetData(
            entity_id="",
            animal_name="Lola",
            birth_year=2023,
            species=AnimalSpecies.DOG,
            gender=AnimalGender.FEMALE,
            size=AnimalSize.MEDIUM,
            sterilized=False,
            vaccinated=False,
            lost=False,
            qr_code="https://.../qr/id_pepito",
            picture="https://.../picture/id_pepito",
            race=None,
            special_care="",
        )

        pet1 = await self.create_pet(
            uow=uow, actor_profile=self.profile1, pet_data=pet_data1
        )
        pet2 = await self.create_pet(
            uow=uow, actor_profile=self.profile1, pet_data=pet_data2
        )
        pet3 = await self.create_pet(
            uow=uow, actor_profile=self.profile2, pet_data=pet_data3
        )
        pet4 = await self.create_pet(
            uow=uow, actor_profile=self.profile2, pet_data=pet_data4
        )

        pets_not_ordered: list[PetDataForTesting] = [
            pet1,
            pet2,
            pet3,
            pet4,
        ]
        self.pets = sorted(
            pets_not_ordered,
            key=lambda pet: pet.pet_data.animal_name,
        )

    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.use_case: GetPetsUseCase = self.dependencies.resolve(GetPetsUseCase)
        self.pets_service = self.dependencies.resolve(PetService)

        await self.initial_data()

    async def test_get_pets_success(self) -> None:
        list_view: PetListView = await self.use_case.execute(
            GetPetsUseCase.Request(
                limit=self.TEST_NO_LIMIT,
                offset=self.TEST_OFFSET_ZERO,
                lost=None,
                profile_id=None,
            )
        )

        self.assertEqual(len(self.pets), list_view.total_count)

        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            for i in range(len(list_view.items)):
                pet_data = self.pets[i].pet_data
                owner = await self.get_personal_profile(
                    uow=uow, profile_id=self.pets[i].profile_id
                )
                owner_name = owner.first_name + " " + owner.surname

                self.assertEqual(
                    (
                        pet_data.entity_id,
                        pet_data.animal_name,
                        pet_data.birth_year,
                        pet_data.species,
                        pet_data.gender,
                        pet_data.size,
                        pet_data.sterilized,
                        pet_data.vaccinated,
                        pet_data.lost,
                        owner_name,
                        pet_data.qr_code,
                        pet_data.picture,
                        pet_data.race,
                        pet_data.special_care,
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
                        list_view.items[i].lost,
                        list_view.items[i].owner_name,
                        list_view.items[i].qr_code,
                        list_view.items[i].picture,
                        list_view.items[i].race,
                        list_view.items[i].special_care,
                    ),
                )

    async def test_get_pets_pagination_with_limit(self) -> None:
        list_view: PetListView = await self.use_case.execute(
            GetPetsUseCase.Request(
                limit=self.TEST_LIMIT,
                offset=self.TEST_OFFSET_ZERO,
                lost=None,
                profile_id=None,
            )
        )

        self.assertEqual(len(self.pets), list_view.total_count)
        self.assertEqual(self.TEST_LIMIT, len(list_view.items))

        for i in range(self.TEST_LIMIT):
            pet_data = self.pets[i].pet_data
            self.assertEqual(
                (
                    pet_data.entity_id,
                    pet_data.animal_name,
                    pet_data.birth_year,
                    pet_data.species,
                    pet_data.gender,
                    pet_data.size,
                    pet_data.sterilized,
                    pet_data.vaccinated,
                    pet_data.lost,
                    pet_data.qr_code,
                    pet_data.picture,
                    pet_data.race,
                    pet_data.special_care,
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
                    list_view.items[i].lost,
                    list_view.items[i].qr_code,
                    list_view.items[i].picture,
                    list_view.items[i].race,
                    list_view.items[i].special_care,
                ),
            )

    async def test_get_pets_pagination_with_offset(self) -> None:
        list_view: PetListView = await self.use_case.execute(
            GetPetsUseCase.Request(
                limit=None, offset=self.TEST_OFFSET, lost=None, profile_id=None
            )
        )

        self.assertEqual(len(self.pets), list_view.total_count)
        index_offset = self.TEST_OFFSET

        for pet in list_view.items:
            pet_data = self.pets[index_offset].pet_data
            self.assertEqual(
                (
                    pet_data.entity_id,
                    pet_data.animal_name,
                    pet_data.birth_year,
                    pet_data.species,
                    pet_data.gender,
                    pet_data.size,
                    pet_data.sterilized,
                    pet_data.vaccinated,
                    pet_data.lost,
                    pet_data.qr_code,
                    pet_data.picture,
                    pet_data.race,
                    pet_data.special_care,
                ),
                (
                    pet.entity_id,
                    pet.animal_name,
                    pet.birth_year,
                    pet.species,
                    pet.gender,
                    pet.size,
                    pet.sterilized,
                    pet.vaccinated,
                    pet.lost,
                    pet.qr_code,
                    pet.picture,
                    pet.race,
                    pet.special_care,
                ),
            )
            index_offset += 1

    async def test_get_lost_pets(self) -> None:
        list_view: PetListView = await self.use_case.execute(
            GetPetsUseCase.Request(
                limit=None, offset=self.TEST_OFFSET_ZERO, lost=True, profile_id=None
            )
        )

        lost_pets = [pet.pet_data for pet in self.pets if pet.pet_data.lost]
        self.assertEqual(len(lost_pets), list_view.total_count)

        for i in range(len(list_view.items)):
            self.assertEqual(
                (
                    lost_pets[i].entity_id,
                    lost_pets[i].animal_name,
                    lost_pets[i].birth_year,
                    lost_pets[i].species,
                    lost_pets[i].gender,
                    lost_pets[i].size,
                    lost_pets[i].sterilized,
                    lost_pets[i].vaccinated,
                    lost_pets[i].lost,
                    lost_pets[i].qr_code,
                    lost_pets[i].picture,
                    lost_pets[i].race,
                    lost_pets[i].special_care,
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
                    list_view.items[i].lost,
                    list_view.items[i].qr_code,
                    list_view.items[i].picture,
                    list_view.items[i].race,
                    list_view.items[i].special_care,
                ),
            )

    async def test_get_not_lost_pets(self) -> None:
        list_view: PetListView = await self.use_case.execute(
            GetPetsUseCase.Request(
                limit=None, offset=self.TEST_OFFSET_ZERO, lost=False, profile_id=None
            )
        )

        lost_pets = [pet.pet_data for pet in self.pets if not pet.pet_data.lost]
        self.assertEqual(len(lost_pets), list_view.total_count)

        for i in range(len(list_view.items)):
            self.assertEqual(
                (
                    lost_pets[i].entity_id,
                    lost_pets[i].animal_name,
                    lost_pets[i].birth_year,
                    lost_pets[i].species,
                    lost_pets[i].gender,
                    lost_pets[i].size,
                    lost_pets[i].sterilized,
                    lost_pets[i].vaccinated,
                    lost_pets[i].lost,
                    lost_pets[i].qr_code,
                    lost_pets[i].picture,
                    lost_pets[i].race,
                    lost_pets[i].special_care,
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
                    list_view.items[i].lost,
                    list_view.items[i].qr_code,
                    list_view.items[i].picture,
                    list_view.items[i].race,
                    list_view.items[i].special_care,
                ),
            )

    async def test_get_lost_pets_from_owner(self) -> None:
        list_view: PetListView = await self.use_case.execute(
            GetPetsUseCase.Request(
                limit=None,
                offset=self.TEST_OFFSET_ZERO,
                lost=True,
                profile_id=self.profile1.profile_id,
            )
        )

        lost_pets_from_owner = [
            pet.pet_data
            for pet in self.pets
            if pet.pet_data.lost and pet.profile_id == self.profile1.profile_id
        ]
        self.assertEqual(len(lost_pets_from_owner), list_view.total_count)

        for i in range(len(list_view.items)):
            self.assertEqual(
                (
                    lost_pets_from_owner[i].entity_id,
                    lost_pets_from_owner[i].animal_name,
                    lost_pets_from_owner[i].birth_year,
                    lost_pets_from_owner[i].species,
                    lost_pets_from_owner[i].gender,
                    lost_pets_from_owner[i].size,
                    lost_pets_from_owner[i].sterilized,
                    lost_pets_from_owner[i].vaccinated,
                    lost_pets_from_owner[i].lost,
                    lost_pets_from_owner[i].qr_code,
                    lost_pets_from_owner[i].picture,
                    lost_pets_from_owner[i].race,
                    lost_pets_from_owner[i].special_care,
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
                    list_view.items[i].lost,
                    list_view.items[i].qr_code,
                    list_view.items[i].picture,
                    list_view.items[i].race,
                    list_view.items[i].special_care,
                ),
            )

    async def test_get_not_lost_pets_from_owner(self) -> None:
        list_view: PetListView = await self.use_case.execute(
            GetPetsUseCase.Request(
                limit=None,
                offset=self.TEST_OFFSET_ZERO,
                lost=False,
                profile_id=self.profile2.profile_id,
            )
        )

        lost_pets = [
            pet.pet_data
            for pet in self.pets
            if not pet.pet_data.lost and pet.profile_id == self.profile2.profile_id
        ]
        self.assertEqual(len(lost_pets), list_view.total_count)

        for i in range(len(list_view.items)):
            self.assertEqual(
                (
                    lost_pets[i].entity_id,
                    lost_pets[i].animal_name,
                    lost_pets[i].birth_year,
                    lost_pets[i].species,
                    lost_pets[i].gender,
                    lost_pets[i].size,
                    lost_pets[i].sterilized,
                    lost_pets[i].vaccinated,
                    lost_pets[i].lost,
                    lost_pets[i].qr_code,
                    lost_pets[i].picture,
                    lost_pets[i].race,
                    lost_pets[i].special_care,
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
                    list_view.items[i].lost,
                    list_view.items[i].qr_code,
                    list_view.items[i].picture,
                    list_view.items[i].race,
                    list_view.items[i].special_care,
                ),
            )
