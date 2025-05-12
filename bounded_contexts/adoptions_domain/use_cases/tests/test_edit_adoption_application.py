from datetime import datetime
from typing import Sequence

from freezegun import freeze_time

from bounded_contexts.adoptions_domain.enum import (
    AdoptionApplicationStates,
    AdoptionAnimalStates,
)
from bounded_contexts.adoptions_domain.exceptions import (
    AdoptionAnimalApplicationUnauthorizedAccessException,
    AnimalAlreadyAdoptedException,
    AdoptionApplicationAlreadyClosedException,
)
from bounded_contexts.adoptions_domain.services.adoption_applications_service import (
    ModifyAdoptionApplicationData,
    AdoptionApplicationData,
)
from bounded_contexts.adoptions_domain.services.adoption_service import AdoptionData
from bounded_contexts.adoptions_domain.services.adoptions_animals_service import (
    AdoptionAnimalData,
)
from bounded_contexts.adoptions_domain.use_cases.edit_adoption_application import (
    EditAdoptionApplicationUseCase,
)
from bounded_contexts.adoptions_domain.views import AdoptionApplicationView
from common.testing import BaseUseCaseTest
from common.testing.base_testing_utils import BaseTestingUtils
from infrastructure.date_utils import datetime_now_tz
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work, make_unit_of_work


class TestEditAdoptionApplication(BaseUseCaseTest, BaseTestingUtils):
    @unit_of_work
    async def initial_data(self, uow: UnitOfWork) -> None:
        self.adoption_giver_personal_profile = await self.create_profile(uow=uow)
        self.adoption_giver_organizational_profile = (
            await self.create_organizational_profile(uow=uow)
        )
        self.collaborator_profile = await self.create_organizational_collaborator_profile(
            uow=uow,
            organization_id=self.adoption_giver_organizational_profile.organization.entity_id,
            account_email="collaborator@gmail.com",
        )
        self.adopter_profile = await self.create_profile(uow=uow)

        self.animal_data_personal_profile = (
            await self.create_adoption_animal(
                uow=uow, actor_profile=self.adoption_giver_personal_profile
            )
        ).adoption_animal_data

        self.adoption_application_personal_profile = (
            await self.create_adoption_application(
                uow=uow,
                actor_profile=self.adopter_profile,
                animal_id=self.animal_data_personal_profile.entity_id,
            )
        )

        self.animal_data_organizational_profile = (
            await self.create_adoption_animal(
                uow=uow,
                actor_profile=self.adoption_giver_organizational_profile.profile_data,
            )
        ).adoption_animal_data

        self.adoption_application_organizational_profile = (
            await self.create_adoption_application(
                uow=uow,
                actor_profile=self.adopter_profile,
                animal_id=self.animal_data_organizational_profile.entity_id,
            )
        )

    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.use_case: EditAdoptionApplicationUseCase = self.dependencies.resolve(
            EditAdoptionApplicationUseCase
        )

        await self.initial_data()

    async def test_edit_personal_profile_adoption_application_reject_success(
        self,
    ) -> None:
        new_adoption_application_data = ModifyAdoptionApplicationData(
            entity_id=self.adoption_application_personal_profile.adoption_application_data.entity_id,
            state=AdoptionApplicationStates.REJECTED,
        )

        view: AdoptionApplicationView = await self.use_case.execute(
            EditAdoptionApplicationUseCase.Request(
                actor_account_id=self.adoption_giver_personal_profile.account_id,
                application_data=new_adoption_application_data,
            )
        )

        self.assertEqual(
            new_adoption_application_data,
            ModifyAdoptionApplicationData(entity_id=view.entity_id, state=view.state),
        )

        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            self.assertEqual(
                AdoptionApplicationData(
                    entity_id=view.entity_id,
                    state=view.state,
                    ever_had_pet=view.ever_had_pet,
                    has_pet=view.has_pet,
                    type_of_housing=view.type_of_housing,
                    pet_time_commitment=view.pet_time_commitment,
                    adoption_info=view.adoption_info,
                    adopter_profile_id=view.adopter_profile_id,
                    animal_id=view.animal_id,
                    open_space=view.open_space,
                    application_date=view.application_date,
                    safety_in_open_spaces=view.safety_in_open_spaces,
                    animal_nice_to_others=view.animal_nice_to_others,
                ),
                await self.get_adoption_application(
                    uow=uow,
                    adoption_application_id=self.adoption_application_personal_profile.adoption_application_data.entity_id,
                ),
            )

    async def test_edit_foreign_adoption_application_fails(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            foreign_profile = await self.create_profile(uow=uow)

        new_adoption_application_data = ModifyAdoptionApplicationData(
            entity_id=self.adoption_application_personal_profile.adoption_application_data.entity_id,
            state=AdoptionApplicationStates.ACCEPTED,
        )

        with self.assertRaises(AdoptionAnimalApplicationUnauthorizedAccessException):
            await self.use_case.execute(
                EditAdoptionApplicationUseCase.Request(
                    actor_account_id=foreign_profile.account_id,
                    application_data=new_adoption_application_data,
                )
            )

    async def test_edit_organizational_adoption_application_accepted_success(
        self,
    ) -> None:
        application: AdoptionApplicationData = (
            self.adoption_application_organizational_profile.adoption_application_data
        )

        new_adoption_application_data = ModifyAdoptionApplicationData(
            entity_id=application.entity_id,
            state=AdoptionApplicationStates.ACCEPTED,
        )

        with freeze_time(
            datetime(year=2023, month=10, day=12, hour=10, minute=46, second=30)
        ):
            view: AdoptionApplicationView = await self.use_case.execute(
                EditAdoptionApplicationUseCase.Request(
                    actor_account_id=self.collaborator_profile.profile_data.account_id,
                    application_data=new_adoption_application_data,
                )
            )

            self.assertEqual(
                new_adoption_application_data,
                ModifyAdoptionApplicationData(
                    entity_id=view.entity_id, state=view.state
                ),
            )

            # assert: application updated
            async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
                self.assertEqual(
                    AdoptionApplicationData(
                        entity_id=view.entity_id,
                        state=view.state,
                        ever_had_pet=view.ever_had_pet,
                        has_pet=view.has_pet,
                        type_of_housing=view.type_of_housing,
                        pet_time_commitment=view.pet_time_commitment,
                        adoption_info=view.adoption_info,
                        adopter_profile_id=view.adopter_profile_id,
                        animal_id=view.animal_id,
                        open_space=view.open_space,
                        application_date=view.application_date,
                        safety_in_open_spaces=view.safety_in_open_spaces,
                        animal_nice_to_others=view.animal_nice_to_others,
                    ),
                    await self.get_adoption_application(
                        uow=uow,
                        adoption_application_id=application.entity_id,
                    ),
                )

                # assert: adoption created
                adoption: AdoptionData = await self.get_adoption(
                    uow=uow, adoption_application_id=application.entity_id
                )
                self.assertEqual(datetime_now_tz(), adoption.adoption_date)

                # assert: animal state updated
                animal: AdoptionAnimalData = await self.get_all_adoption_animal(
                    uow=uow,
                    adoption_animal_id=self.animal_data_organizational_profile.entity_id,
                )
                self.assertEqual(AdoptionAnimalStates.ADOPTED, animal.state)

                # assert: other applications rejected
                adoption_applications_for_animal: Sequence[
                    AdoptionApplicationData
                ] = await self.get_adoption_applications_by_animal_id(
                    uow=uow,
                    adoption_animal_id=self.animal_data_organizational_profile.entity_id,
                )

                adoption_applications_for_animal_should_be_rejected = [
                    adoption_application
                    for adoption_application in adoption_applications_for_animal
                    if adoption_application.entity_id != application.entity_id
                ]

                for i in range(
                    len(adoption_applications_for_animal_should_be_rejected)
                ):
                    adoption_application = (
                        adoption_applications_for_animal_should_be_rejected[i]
                    )
                    self.assertEqual(
                        AdoptionApplicationStates.REJECTED, adoption_application.state
                    )

    async def test_edit_adoption_application_for_already_adopted_animal_fails(
        self,
    ) -> None:
        new_adoption_application_data = ModifyAdoptionApplicationData(
            entity_id=self.adoption_application_organizational_profile.adoption_application_data.entity_id,
            state=AdoptionApplicationStates.ACCEPTED,
        )

        await self.use_case.execute(
            EditAdoptionApplicationUseCase.Request(
                actor_account_id=self.collaborator_profile.profile_data.account_id,
                application_data=new_adoption_application_data,
            )
        )

        new_adoption_application_data = ModifyAdoptionApplicationData(
            entity_id=self.adoption_application_organizational_profile.adoption_application_data.entity_id,
            state=AdoptionApplicationStates.REJECTED,
        )

        with self.assertRaises(AnimalAlreadyAdoptedException):
            await self.use_case.execute(
                EditAdoptionApplicationUseCase.Request(
                    actor_account_id=self.collaborator_profile.profile_data.account_id,
                    application_data=new_adoption_application_data,
                )
            )

    async def test_edit_adoption_application_already_closed_fails(self) -> None:
        new_adoption_application_data = ModifyAdoptionApplicationData(
            entity_id=self.adoption_application_organizational_profile.adoption_application_data.entity_id,
            state=AdoptionApplicationStates.REJECTED,
        )

        await self.use_case.execute(
            EditAdoptionApplicationUseCase.Request(
                actor_account_id=self.collaborator_profile.profile_data.account_id,
                application_data=new_adoption_application_data,
            )
        )

        new_adoption_application_data = ModifyAdoptionApplicationData(
            entity_id=self.adoption_application_organizational_profile.adoption_application_data.entity_id,
            state=AdoptionApplicationStates.ACCEPTED,
        )

        with self.assertRaises(AdoptionApplicationAlreadyClosedException):
            await self.use_case.execute(
                EditAdoptionApplicationUseCase.Request(
                    actor_account_id=self.collaborator_profile.profile_data.account_id,
                    application_data=new_adoption_application_data,
                )
            )

    # TODO: tests for events (application approved) are missing
