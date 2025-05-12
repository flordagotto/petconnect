from uuid import uuid4

from bounded_contexts.pets_domain.entities import PetSight
from bounded_contexts.pets_domain.services import PetData
from bounded_contexts.social_domain.entities.animal import (
    AnimalSpecies,
    AnimalGender,
    AnimalSize,
)
from bounded_contexts.pets_domain.use_cases.get_pet_sights import GetPetSightsUseCase
from bounded_contexts.pets_domain.views.pet_sight_view import PetSightListView
from common.testing import BaseUseCaseTest
from common.testing.base_testing_utils import BaseTestingUtils
from infrastructure.uow_abstraction import unit_of_work, UnitOfWork


class TestGetPetSightsUseCase(BaseUseCaseTest, BaseTestingUtils):
    TEST_NO_LIMIT = None
    TEST_OFFSET_ZERO = 0
    TEST_LIMIT = 2
    TEST_OFFSET = 1

    @unit_of_work
    async def initial_data(self, uow: UnitOfWork) -> None:
        self.profile = await self.create_profile(uow=uow)
        pet_data1 = PetData(
            entity_id=uuid4().hex,
            animal_name="Pepito",
            lost=True,
            birth_year=2019,
            species=AnimalSpecies.DOG,
            gender=AnimalGender.MALE,
            size=AnimalSize.SMALL,
            sterilized=True,
            vaccinated=True,
            picture="https://petconnect.icu/picture/id_pepito",
            qr_code="https://petconnect.icu/qr/id_pepito",
        )

        self.lost_pet_data1 = (
            await self.create_pet(uow=uow, actor_profile=self.profile, lost=True)
        ).pet_data

        self.lost_pet_data2 = (
            await self.create_pet(
                uow=uow, actor_profile=self.profile, pet_data=pet_data1, lost=True
            )
        ).pet_data

        pet_sight1 = await self.create_pet_sight(
            uow=uow,
            pet_id=self.lost_pet_data1.entity_id,
            account_id=self.profile.account_id,
        )
        pet_sight2 = await self.create_pet_sight(
            uow=uow,
            pet_id=self.lost_pet_data2.entity_id,
            account_id=self.profile.account_id,
        )
        pet_sight3 = await self.create_pet_sight(
            uow=uow,
            pet_id=self.lost_pet_data2.entity_id,
            account_id=self.profile.account_id,
        )

        pet_sights_not_ordered: list[PetSight] = [pet_sight1, pet_sight2, pet_sight3]

        self.pet_sights = sorted(
            pet_sights_not_ordered,
            key=lambda pet_sight: pet_sight.created_at,
        )

    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.use_case: GetPetSightsUseCase = self.dependencies.resolve(
            GetPetSightsUseCase
        )

        await self.initial_data()

    async def test_get_pet_sights_success(self) -> None:
        list_view: PetSightListView = await self.use_case.execute(
            GetPetSightsUseCase.Request(
                limit=self.TEST_NO_LIMIT, offset=self.TEST_OFFSET_ZERO
            )
        )

        self.assertEqual(len(self.pet_sights), list_view.total_count)

        for i in range(len(list_view.items)):
            self.assertEqual(
                (
                    self.pet_sights[i].entity_id,
                    self.pet_sights[i].pet_id,
                    self.pet_sights[i].latitude,
                    self.pet_sights[i].longitude,
                    self.pet_sights[i].created_at,
                    self.pet_sights[i].account_id,
                ),
                (
                    list_view.items[i].entity_id,
                    list_view.items[i].pet_id,
                    list_view.items[i].latitude,
                    list_view.items[i].longitude,
                    list_view.items[i].created_at,
                    list_view.items[i].account_id,
                ),
            )

    async def test_get_pet_sights_pagination_with_limit(self) -> None:
        list_view: PetSightListView = await self.use_case.execute(
            GetPetSightsUseCase.Request(
                limit=self.TEST_LIMIT, offset=self.TEST_OFFSET_ZERO
            )
        )

        self.assertEqual(len(self.pet_sights), list_view.total_count)
        self.assertEqual(self.TEST_LIMIT, len(list_view.items))

        for i in range(self.TEST_LIMIT):
            self.assertEqual(
                (
                    self.pet_sights[i].entity_id,
                    self.pet_sights[i].pet_id,
                    self.pet_sights[i].latitude,
                    self.pet_sights[i].longitude,
                    self.pet_sights[i].created_at,
                    self.pet_sights[i].account_id,
                ),
                (
                    list_view.items[i].entity_id,
                    list_view.items[i].pet_id,
                    list_view.items[i].latitude,
                    list_view.items[i].longitude,
                    list_view.items[i].created_at,
                    list_view.items[i].account_id,
                ),
            )

    async def test_get_pet_sights_pagination_with_offset(self) -> None:
        list_view: PetSightListView = await self.use_case.execute(
            GetPetSightsUseCase.Request(limit=None, offset=self.TEST_OFFSET)
        )

        self.assertEqual(len(self.pet_sights), list_view.total_count)
        index_offset = self.TEST_OFFSET

        for pet_sight in list_view.items:
            self.assertEqual(
                (
                    self.pet_sights[index_offset].entity_id,
                    self.pet_sights[index_offset].pet_id,
                    self.pet_sights[index_offset].latitude,
                    self.pet_sights[index_offset].longitude,
                    self.pet_sights[index_offset].created_at,
                    self.pet_sights[index_offset].account_id,
                ),
                (
                    pet_sight.entity_id,
                    pet_sight.pet_id,
                    pet_sight.latitude,
                    pet_sight.longitude,
                    pet_sight.created_at,
                    pet_sight.account_id,
                ),
            )
            index_offset += 1

    async def test_get_pet_sights_by_pet_id(self) -> None:
        list_view: PetSightListView = await self.use_case.execute(
            GetPetSightsUseCase.Request(
                limit=None,
                offset=self.TEST_OFFSET_ZERO,
                pet_id=self.lost_pet_data2.entity_id,
            )
        )

        pet_sights_for_pet2 = [
            pet_sight
            for pet_sight in self.pet_sights
            if pet_sight.pet_id == self.lost_pet_data2.entity_id
        ]
        self.assertEqual(len(pet_sights_for_pet2), list_view.total_count)

        for i in range(len(list_view.items)):
            self.assertEqual(
                (
                    pet_sights_for_pet2[i].entity_id,
                    pet_sights_for_pet2[i].pet_id,
                    pet_sights_for_pet2[i].latitude,
                    pet_sights_for_pet2[i].longitude,
                    pet_sights_for_pet2[i].created_at,
                    pet_sights_for_pet2[i].account_id,
                ),
                (
                    list_view.items[i].entity_id,
                    list_view.items[i].pet_id,
                    list_view.items[i].latitude,
                    list_view.items[i].longitude,
                    list_view.items[i].created_at,
                    list_view.items[i].account_id,
                ),
            )
