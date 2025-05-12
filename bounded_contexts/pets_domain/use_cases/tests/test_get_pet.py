from bounded_contexts.pets_domain.exceptions import PetNotFoundByIdException
from bounded_contexts.pets_domain.use_cases import GetPetUseCase
from bounded_contexts.pets_domain.views import PetAndOwnerView
from common.testing import BaseUseCaseTest
from common.testing.base_testing_utils import BaseTestingUtils
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work, make_unit_of_work


class TestGetPet(BaseUseCaseTest, BaseTestingUtils):
    TEST_PET_ID: str = "12345"

    @unit_of_work
    async def initial_data(self, uow: UnitOfWork) -> None:
        self.profile = await self.create_profile(uow=uow)
        self.pet_data = (
            await self.create_pet(uow=uow, actor_profile=self.profile)
        ).pet_data

    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.use_case: GetPetUseCase = self.dependencies.resolve(GetPetUseCase)

        await self.initial_data()

    async def test_get_pet_success(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            pet_and_owner: PetAndOwnerView = await self.use_case.execute(
                entity_id=self.pet_data.entity_id, uow=uow
            )

        pet = pet_and_owner.pet_view
        owner = pet_and_owner.owner_view

        self.assertEqual(
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
                pet.qr_code,  # this assertion will fail because of the qr code - it's not finished yet
                pet.picture,
                pet.race,
                pet.special_care,
            ),
            (
                self.pet_data.entity_id,
                self.pet_data.animal_name,
                self.pet_data.birth_year,
                self.pet_data.species,
                self.pet_data.gender,
                self.pet_data.size,
                self.pet_data.sterilized,
                self.pet_data.vaccinated,
                self.pet_data.lost,
                self.pet_data.qr_code,
                self.pet_data.picture,
                self.pet_data.race,
                self.pet_data.special_care,
            ),
        )

    async def test_get_pet_fails(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            with self.assertRaises(PetNotFoundByIdException):
                await self.pet_service.get_pet_by_id(
                    uow=uow, entity_id=self.TEST_PET_ID
                )
