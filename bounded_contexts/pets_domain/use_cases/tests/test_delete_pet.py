from bounded_contexts.social_domain.entities import (
    AnimalSpecies,
    AnimalGender,
    AnimalSize,
)
from bounded_contexts.pets_domain.exceptions import (
    PetUnauthorizedAccessException,
    PetNotFoundByIdException,
)
from bounded_contexts.pets_domain.services.pet_service import PetData
from bounded_contexts.pets_domain.use_cases import DeletePetUseCase
from common.testing import BaseUseCaseTest
from common.testing.base_testing_utils import BaseTestingUtils
from infrastructure.uow_abstraction import make_unit_of_work, UnitOfWork, unit_of_work


class TestDeletePet(BaseUseCaseTest, BaseTestingUtils):
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

        self.pet1 = await self.create_pet(
            uow=uow, actor_profile=self.profile1, pet_data=pet_data1
        )
        self.pet2 = await self.create_pet(
            uow=uow, actor_profile=self.profile1, pet_data=pet_data2
        )
        self.pet3 = await self.create_pet(
            uow=uow, actor_profile=self.profile2, pet_data=pet_data3
        )

        self.pet_sight = await self.create_pet_sight(
            uow=uow,
            pet_id=pet_data3.entity_id,
            account_id=self.profile2.account_id,
        )

    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.use_case: DeletePetUseCase = self.dependencies.resolve(DeletePetUseCase)

        await self.initial_data()

    async def test_delete_pet_without_sights_success(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            pet_data: PetData = await self.get_pet(
                uow=uow, pet_id=self.pet1.pet_data.entity_id
            )

            await self.use_case.execute(
                DeletePetUseCase.Request(
                    entity_id=pet_data.entity_id,
                    actor_account_id=self.profile1.account_id,
                )
            )

            with self.assertRaises(PetNotFoundByIdException):
                await self.get_pet(uow=uow, pet_id=self.pet1.pet_data.entity_id)

    async def test_delete_pet_with_sights_success(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            pet_data: PetData = await self.get_pet(
                uow=uow, pet_id=self.pet3.pet_data.entity_id
            )

            await self.use_case.execute(
                DeletePetUseCase.Request(
                    entity_id=pet_data.entity_id,
                    actor_account_id=self.profile2.account_id,
                )
            )

            pet_sights = await self.get_pet_sights_by_pet_id(
                uow=uow, pet_id=self.pet3.pet_data.entity_id
            )

            self.assertEqual(pet_sights, [])

            with self.assertRaises(PetNotFoundByIdException):
                await self.get_pet(uow=uow, pet_id=self.pet3.pet_data.entity_id)

    async def test_delete_pet_fails(self) -> None:
        with self.assertRaises(PetNotFoundByIdException):
            await self.use_case.execute(
                DeletePetUseCase.Request(
                    entity_id="12345", actor_account_id=self.profile1.account_id
                )
            )

    async def test_delete_foreign_pet_fails(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            pet_data: PetData = await self.get_pet(
                uow=uow, pet_id=self.pet1.pet_data.entity_id
            )

        with self.assertRaises(PetUnauthorizedAccessException):
            await self.use_case.execute(
                DeletePetUseCase.Request(
                    entity_id=pet_data.entity_id,
                    actor_account_id=self.profile2.account_id,
                )
            )
