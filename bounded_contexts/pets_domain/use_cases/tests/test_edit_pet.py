from datetime import date

from bounded_contexts.social_domain.entities import (
    AnimalSpecies,
    AnimalSize,
    AnimalGender,
)
from bounded_contexts.pets_domain.exceptions import PetUnauthorizedAccessException
from bounded_contexts.pets_domain.services.pet_service import (
    PetData,
    ModifyPetData,
)
from bounded_contexts.pets_domain.use_cases import EditPetUseCase
from bounded_contexts.pets_domain.views import PetView
from common.testing import BaseUseCaseTest
from common.testing.base_testing_utils import BaseTestingUtils
from infrastructure.date_utils import date_now
from infrastructure.uow_abstraction import make_unit_of_work, UnitOfWork, unit_of_work


class TestEditPet(BaseUseCaseTest, BaseTestingUtils):
    @unit_of_work
    async def initial_data(self, uow: UnitOfWork) -> None:
        self.profile = await self.create_profile(uow=uow)
        self.pet_data = (
            await self.create_pet(uow=uow, actor_profile=self.profile)
        ).pet_data

    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.use_case: EditPetUseCase = self.dependencies.resolve(EditPetUseCase)

        await self.initial_data()

    async def test_edit_pet_success(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            pet_data: PetData = await self.get_pet(
                uow=uow, pet_id=self.pet_data.entity_id
            )

            self.assertEqual(self.pet_data, pet_data)

        new_pet_data = ModifyPetData(
            entity_id=self.pet_data.entity_id,
            animal_name="new pet name hehe",
            lost=True,
            birth_year=2005,
            species=AnimalSpecies.CAT,
            gender=AnimalGender.FEMALE,
            size=AnimalSize.MEDIUM,
            sterilized=False,
            vaccinated=True,
            lost_date=date_now(),
            picture="https://petconnect.icu/picture/id_pepito_2.jpg",
            last_known_latitude=-34.603722,
            last_known_longitude=-58.381592,
            last_known_location="Buenos Aires, Argentina",
        )

        view: PetView = await self.use_case.execute(
            EditPetUseCase.Request(
                actor_account_id=self.profile.account_id,
                pet_data=new_pet_data,
            )
        )

        self.assertEqual(
            new_pet_data,
            ModifyPetData(
                entity_id=view.entity_id,
                animal_name=view.animal_name,
                lost=view.lost,
                birth_year=view.birth_year,
                species=view.species,
                gender=view.gender,
                size=view.size,
                sterilized=view.sterilized,
                vaccinated=view.vaccinated,
                lost_date=view.lost_date,
                picture=view.picture,
                last_known_latitude=-34.603722,
                last_known_longitude=-58.381592,
                last_known_location="Buenos Aires, Argentina",
            ),
        )

        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            self.assertEqual(
                PetData(
                    entity_id=view.entity_id,
                    animal_name=view.animal_name,
                    lost=view.lost,
                    birth_year=view.birth_year,
                    species=view.species,
                    gender=view.gender,
                    size=view.size,
                    sterilized=view.sterilized,
                    vaccinated=view.vaccinated,
                    lost_date=view.lost_date,
                    picture=view.picture,
                    qr_code=view.qr_code,
                ),
                await self.get_pet(uow=uow, pet_id=self.pet_data.entity_id),
            )

            pet_sights = await self.pet_sight_service.get_all_pet_sights(
                uow=uow, pet_id=self.pet_data.entity_id
            )

            self.assertEqual(-34.603722, pet_sights[0].latitude)
            self.assertEqual(-58.381592, pet_sights[0].longitude)

    async def test_edit_pet_with_lost_date_success(self) -> None:
        lost_date = date(2024, 5, 15)
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            pet_data: PetData = await self.get_pet(
                uow=uow, pet_id=self.pet_data.entity_id
            )

            self.assertEqual(self.pet_data, pet_data)

        new_pet_data = ModifyPetData(
            entity_id=self.pet_data.entity_id,
            animal_name="new pet name hehe",
            lost=True,
            birth_year=2005,
            species=AnimalSpecies.CAT,
            gender=AnimalGender.FEMALE,
            size=AnimalSize.MEDIUM,
            sterilized=False,
            vaccinated=True,
            lost_date=lost_date,
            picture="https://petconnect.icu/picture/id_pepito_2.jpg",
            last_known_latitude=-34.603722,
            last_known_longitude=-58.381592,
            last_known_location="Buenos Aires, Argentina",
        )

        view: PetView = await self.use_case.execute(
            EditPetUseCase.Request(
                actor_account_id=self.profile.account_id,
                pet_data=new_pet_data,
            )
        )

        self.assertEqual(
            new_pet_data,
            ModifyPetData(
                entity_id=view.entity_id,
                animal_name=view.animal_name,
                lost=view.lost,
                birth_year=view.birth_year,
                species=view.species,
                gender=view.gender,
                size=view.size,
                sterilized=view.sterilized,
                vaccinated=view.vaccinated,
                picture=view.picture,
                lost_date=view.lost_date,
                last_known_latitude=-34.603722,
                last_known_longitude=-58.381592,
                last_known_location="Buenos Aires, Argentina",
            ),
        )

        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            self.assertEqual(
                PetData(
                    entity_id=view.entity_id,
                    animal_name=view.animal_name,
                    lost=view.lost,
                    birth_year=view.birth_year,
                    species=view.species,
                    gender=view.gender,
                    size=view.size,
                    sterilized=view.sterilized,
                    vaccinated=view.vaccinated,
                    picture=view.picture,
                    lost_date=view.lost_date,
                    qr_code=view.qr_code,
                ),
                await self.get_pet(uow=uow, pet_id=self.pet_data.entity_id),
            )

            pet_sights = await self.pet_sight_service.get_all_pet_sights(
                uow=uow, pet_id=self.pet_data.entity_id
            )

            self.assertEqual(-34.603722, pet_sights[0].latitude)
            self.assertEqual(-58.381592, pet_sights[0].longitude)

    async def test_edit_foreign_pet_fails(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            foreign_profile = await self.create_profile(uow=uow)

        new_pet_data = ModifyPetData(
            entity_id=self.pet_data.entity_id,
            animal_name="new pet name hehe",
            lost=False,
            birth_year=2002,
            species=AnimalSpecies.OTHER,
            gender=AnimalGender.FEMALE,
            size=AnimalSize.BIG,
            sterilized=False,
            vaccinated=False,
            picture="https://petconnect.icu/picture/id_pepito_3.jpg",
        )
        with self.assertRaises(PetUnauthorizedAccessException):
            await self.use_case.execute(
                EditPetUseCase.Request(
                    actor_account_id=foreign_profile.account_id,
                    pet_data=new_pet_data,
                )
            )
