from bounded_contexts.pets_domain.entities import PetSight
from bounded_contexts.pets_domain.exceptions import SightForNotLostPetException
from bounded_contexts.pets_domain.use_cases import (
    RegisterPetSightUseCase,
)
from bounded_contexts.pets_domain.views import PetSightView
from common.testing import BaseUseCaseTest
from common.testing.base_testing_utils import BaseTestingUtils
from infrastructure.date_utils import datetime_now_tz
from infrastructure.uow_abstraction import make_unit_of_work, unit_of_work, UnitOfWork
import datetime


class TestCreatePetSight(BaseUseCaseTest, BaseTestingUtils):
    @unit_of_work
    async def initial_data(self, uow: UnitOfWork) -> None:
        self.profile = await self.create_profile(uow=uow)

        self.lost_pet_data = (
            await self.create_pet(uow=uow, actor_profile=self.profile, lost=True)
        ).pet_data

        self.not_lost_pet_data = (
            await self.create_pet(uow=uow, actor_profile=self.profile)
        ).pet_data

    TEST_LATITUDE: float = 35.70407437075822
    TEST_LONGITUDE: float = 139.5577317304603
    TEST_CREATED_AT: datetime.datetime = datetime_now_tz()
    TEST_ACCOUNT_ID_NONE: None = None

    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.use_case: RegisterPetSightUseCase = self.dependencies.resolve(
            RegisterPetSightUseCase
        )

        await self.initial_data()

    async def test_register_pet_sight_anonymous_user_success(self) -> None:
        view: PetSightView = await self.use_case.execute(
            RegisterPetSightUseCase.Request(
                pet_id=self.lost_pet_data.entity_id,
                latitude=self.TEST_LATITUDE,
                longitude=self.TEST_LONGITUDE,
                account_id=self.TEST_ACCOUNT_ID_NONE,
            )
        )

        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            pet_sight: PetSight = await self.pet_sight_service.get_pet_sight_by_id(
                uow=uow, entity_id=view.entity_id
            )

            self.assertEqual(
                (
                    pet_sight.entity_id,
                    pet_sight.pet_id,
                    pet_sight.latitude,
                    pet_sight.longitude,
                    pet_sight.account_id,
                    pet_sight.created_at,
                ),
                (
                    view.entity_id,
                    view.pet_id,
                    view.latitude,
                    view.longitude,
                    view.account_id,
                    view.created_at,
                ),
            )

    async def test_register_pet_sight_with_account_success(self) -> None:
        view: PetSightView = await self.use_case.execute(
            RegisterPetSightUseCase.Request(
                pet_id=self.lost_pet_data.entity_id,
                latitude=self.TEST_LATITUDE,
                longitude=self.TEST_LONGITUDE,
                account_id=self.profile.account_id,
            )
        )

        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            pet_sight: PetSight = await self.pet_sight_service.get_pet_sight_by_id(
                uow=uow, entity_id=view.entity_id
            )

            self.assertEqual(
                (
                    pet_sight.entity_id,
                    pet_sight.pet_id,
                    pet_sight.latitude,
                    pet_sight.longitude,
                    pet_sight.account_id,
                    pet_sight.created_at,
                ),
                (
                    view.entity_id,
                    view.pet_id,
                    view.latitude,
                    view.longitude,
                    view.account_id,
                    view.created_at,
                ),
            )

    async def test_register_pet_sight_fail(self) -> None:
        with self.assertRaises(SightForNotLostPetException):
            await self.use_case.execute(
                RegisterPetSightUseCase.Request(
                    pet_id=self.not_lost_pet_data.entity_id,
                    latitude=self.TEST_LATITUDE,
                    longitude=self.TEST_LONGITUDE,
                    account_id=self.TEST_ACCOUNT_ID_NONE,
                )
            )
