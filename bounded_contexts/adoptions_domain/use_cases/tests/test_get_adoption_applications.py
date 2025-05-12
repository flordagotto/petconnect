from datetime import datetime

from freezegun import freeze_time

from bounded_contexts.adoptions_domain.enum import AdoptionAnimalStates
from bounded_contexts.adoptions_domain.services.adoptions_animals_service import (
    AdoptionAnimalData,
)
from bounded_contexts.adoptions_domain.use_cases.get_adoption_applications import (
    GetAdoptionApplicationsUseCase,
)
from bounded_contexts.adoptions_domain.views import AdoptionApplicationListView
from bounded_contexts.social_domain.entities.animal import (
    AnimalSpecies,
    AnimalGender,
    AnimalSize,
)
from common.testing import BaseUseCaseTest
from common.testing.base_testing_utils import (
    BaseTestingUtils,
    AdoptionApplicationDataForTesting,
)
from infrastructure.uow_abstraction import unit_of_work, UnitOfWork


class TestGetAdoptionApplicationsUseCase(BaseUseCaseTest, BaseTestingUtils):
    TEST_NO_LIMIT = None
    TEST_OFFSET_ZERO = 0
    TEST_LIMIT = 2
    TEST_OFFSET = 1

    @unit_of_work
    async def initial_data(self, uow: UnitOfWork) -> None:
        with freeze_time(
            datetime(year=2023, month=10, day=12, hour=10, minute=46, second=30)
        ):
            # profiles
            self.personal_profile = await self.create_profile(uow=uow)
            self.adoption_giver_organizational_profile = (
                await self.create_organizational_profile(uow=uow)
            )
            self.collaborator_profile = await self.create_organizational_collaborator_profile(
                uow=uow,
                organization_id=self.adoption_giver_organizational_profile.organization.entity_id,
                account_email="collaborator@gmail.com",
            )

            self.adopter_profile = await self.create_profile(uow=uow)

            # animals
            animal_data_personal_profile_1 = (
                await self.create_adoption_animal(
                    uow=uow, actor_profile=self.personal_profile
                )
            ).adoption_animal_data

            adoption_animal_data_1 = AdoptionAnimalData(
                entity_id="",
                animal_name="Tale",
                birth_year=2023,
                species=AnimalSpecies.CAT,
                gender=AnimalGender.MALE,
                size=AnimalSize.BIG,
                sterilized=True,
                vaccinated=True,
                picture="https://.../picture/id_tale",
                state=AdoptionAnimalStates.FOR_ADOPTION,
                race="no",
                special_care="no",
            )

            animal_data_personal_profile_2 = (
                await self.create_adoption_animal(
                    uow=uow,
                    actor_profile=self.personal_profile,
                    adoption_animal_data=adoption_animal_data_1,
                )
            ).adoption_animal_data

            animal_data_organizational_profile_1 = (
                await self.create_adoption_animal(
                    uow=uow,
                    actor_profile=self.adoption_giver_organizational_profile.profile_data,
                )
            ).adoption_animal_data

            adoption_animal_data_2 = AdoptionAnimalData(
                entity_id="",
                animal_name="Lola",
                birth_year=2023,
                species=AnimalSpecies.DOG,
                gender=AnimalGender.FEMALE,
                size=AnimalSize.BIG,
                sterilized=True,
                vaccinated=True,
                picture="https://.../picture/id_lola",
                state=AdoptionAnimalStates.FOR_ADOPTION,
                race="no",
                special_care="diabetes",
            )

            animal_data_organizational_profile_2 = (
                await self.create_adoption_animal(
                    uow=uow,
                    actor_profile=self.adoption_giver_organizational_profile.profile_data,
                    adoption_animal_data=adoption_animal_data_2,
                )
            ).adoption_animal_data

            # applications
            adoption_application_to_personal_profile_animal_1 = (
                await self.create_adoption_application(
                    uow=uow,
                    actor_profile=self.adopter_profile,
                    animal_id=animal_data_personal_profile_1.entity_id,
                )
            )

        with freeze_time(
            datetime(year=2023, month=10, day=10, hour=15, minute=46, second=30)
        ):
            adoption_application_to_personal_profile_animal_2 = (
                await self.create_adoption_application(
                    uow=uow,
                    actor_profile=self.adopter_profile,
                    animal_id=animal_data_personal_profile_2.entity_id,
                )
            )

        with freeze_time(
            datetime(year=2023, month=10, day=12, hour=16, minute=46, second=30)
        ):
            adoption_application_to_organizational_profile_animal_1 = (
                await self.create_adoption_application(
                    uow=uow,
                    actor_profile=self.adopter_profile,
                    animal_id=animal_data_organizational_profile_1.entity_id,
                )
            )

        with freeze_time(
            datetime(year=2023, month=10, day=12, hour=10, minute=47, second=30)
        ):
            adoption_application_to_organizational_profile_animal_2 = (
                await self.create_adoption_application(
                    uow=uow,
                    actor_profile=self.adopter_profile,
                    animal_id=animal_data_organizational_profile_2.entity_id,
                )
            )

        with freeze_time(
            datetime(year=2023, month=10, day=12, hour=11, minute=46, second=30)
        ):
            adoption_application_to_organizational_profile_animal_3 = (
                await self.create_adoption_application(
                    uow=uow,
                    actor_profile=self.personal_profile,
                    animal_id=animal_data_organizational_profile_1.entity_id,
                )
            )

            applications_sent_by_adopter_profile_not_ordered: list[
                AdoptionApplicationDataForTesting
            ] = [
                adoption_application_to_personal_profile_animal_1,
                adoption_application_to_personal_profile_animal_2,
                adoption_application_to_organizational_profile_animal_1,
                adoption_application_to_organizational_profile_animal_2,
            ]

            self.applications_sent_by_adopter_profile = sorted(
                applications_sent_by_adopter_profile_not_ordered,
                key=lambda application: application.adoption_application_data.application_date,
            )

            applications_received_by_personal_profile_not_ordered: list[
                AdoptionApplicationDataForTesting
            ] = [
                adoption_application_to_personal_profile_animal_1,
                adoption_application_to_personal_profile_animal_2,
            ]

            self.applications_received_by_personal_profile = sorted(
                applications_received_by_personal_profile_not_ordered,
                key=lambda application: application.adoption_application_data.application_date,
            )

            applications_received_by_organization_not_ordered: list[
                AdoptionApplicationDataForTesting
            ] = [
                adoption_application_to_organizational_profile_animal_1,
                adoption_application_to_organizational_profile_animal_2,
                adoption_application_to_organizational_profile_animal_3,
            ]

            self.applications_received_by_organization = sorted(
                applications_received_by_organization_not_ordered,
                key=lambda application: application.adoption_application_data.application_date,
            )

    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.use_case: GetAdoptionApplicationsUseCase = self.dependencies.resolve(
            GetAdoptionApplicationsUseCase
        )

        await self.initial_data()

    async def test_get_all_sent_adoption_applications_success(self) -> None:
        list_view: AdoptionApplicationListView = await self.use_case.execute(
            GetAdoptionApplicationsUseCase.Request(
                account_id=self.adopter_profile.account_id,
                filter_by_sent_applications=True,
                limit=self.TEST_NO_LIMIT,
                offset=self.TEST_OFFSET_ZERO,
            )
        )

        self.assertEqual(
            len(self.applications_sent_by_adopter_profile), list_view.total_count
        )

        for i in range(len(list_view.items)):
            application = self.applications_sent_by_adopter_profile[
                i
            ].adoption_application_data
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
                    application.state,
                    application.application_date,
                    application.open_space,
                    application.safety_in_open_spaces,
                    application.animal_nice_to_others,
                ),
                (
                    list_view.items[i].entity_id,
                    list_view.items[i].ever_had_pet,
                    list_view.items[i].has_pet,
                    list_view.items[i].type_of_housing,
                    list_view.items[i].pet_time_commitment,
                    list_view.items[i].adoption_info,
                    list_view.items[i].adopter_profile_id,
                    list_view.items[i].animal_id,
                    list_view.items[i].state,
                    list_view.items[i].application_date,
                    list_view.items[i].open_space,
                    list_view.items[i].safety_in_open_spaces,
                    list_view.items[i].animal_nice_to_others,
                ),
            )

    async def test_get_all_sent_adoption_applications_pagination_with_limit(
        self,
    ) -> None:
        list_view: AdoptionApplicationListView = await self.use_case.execute(
            GetAdoptionApplicationsUseCase.Request(
                account_id=self.adopter_profile.account_id,
                filter_by_sent_applications=True,
                limit=self.TEST_LIMIT,
                offset=self.TEST_OFFSET_ZERO,
            )
        )

        self.assertEqual(
            len(self.applications_sent_by_adopter_profile), list_view.total_count
        )
        self.assertEqual(self.TEST_LIMIT, len(list_view.items))

        for i in range(self.TEST_LIMIT):
            application = self.applications_sent_by_adopter_profile[
                i
            ].adoption_application_data
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
                    application.state,
                    application.application_date,
                    application.open_space,
                    application.safety_in_open_spaces,
                    application.animal_nice_to_others,
                ),
                (
                    list_view.items[i].entity_id,
                    list_view.items[i].ever_had_pet,
                    list_view.items[i].has_pet,
                    list_view.items[i].type_of_housing,
                    list_view.items[i].pet_time_commitment,
                    list_view.items[i].adoption_info,
                    list_view.items[i].adopter_profile_id,
                    list_view.items[i].animal_id,
                    list_view.items[i].state,
                    list_view.items[i].application_date,
                    list_view.items[i].open_space,
                    list_view.items[i].safety_in_open_spaces,
                    list_view.items[i].animal_nice_to_others,
                ),
            )

    async def test_get_all_sent_adoption_applications_pagination_with_offset(
        self,
    ) -> None:
        list_view: AdoptionApplicationListView = await self.use_case.execute(
            GetAdoptionApplicationsUseCase.Request(
                account_id=self.adopter_profile.account_id,
                filter_by_sent_applications=True,
                limit=None,
                offset=self.TEST_OFFSET,
            )
        )

        self.assertEqual(
            len(self.applications_sent_by_adopter_profile), list_view.total_count
        )
        index_offset = self.TEST_OFFSET

        for application in list_view.items:
            application_data = self.applications_sent_by_adopter_profile[
                index_offset
            ].adoption_application_data
            self.assertEqual(
                (
                    application_data.entity_id,
                    application_data.ever_had_pet,
                    application_data.has_pet,
                    application_data.type_of_housing,
                    application_data.pet_time_commitment,
                    application_data.adoption_info,
                    application_data.adopter_profile_id,
                    application_data.animal_id,
                    application_data.state,
                    application_data.application_date,
                    application_data.open_space,
                    application_data.safety_in_open_spaces,
                    application_data.animal_nice_to_others,
                ),
                (
                    application.entity_id,
                    application.ever_had_pet,
                    application.has_pet,
                    application.type_of_housing,
                    application.pet_time_commitment,
                    application.adoption_info,
                    application.adopter_profile_id,
                    application.animal_id,
                    application.state,
                    application.application_date,
                    application.open_space,
                    application.safety_in_open_spaces,
                    application.animal_nice_to_others,
                ),
            )
            index_offset += 1

    async def test_get_all_sent_adoption_applications_by_organizational_profile_returns_empty(
        self,
    ) -> None:
        list_view: AdoptionApplicationListView = await self.use_case.execute(
            GetAdoptionApplicationsUseCase.Request(
                account_id=self.collaborator_profile.profile_data.account_id,
                filter_by_sent_applications=True,
                limit=None,
                offset=self.TEST_OFFSET,
            )
        )

        self.assertEqual(0, list_view.total_count)
        self.assertFalse(list_view.items)

    async def test_get_all_received_adoption_applications_by_personal_profile_success(
        self,
    ) -> None:
        list_view: AdoptionApplicationListView = await self.use_case.execute(
            GetAdoptionApplicationsUseCase.Request(
                account_id=self.personal_profile.account_id,
                filter_by_sent_applications=False,
                limit=self.TEST_NO_LIMIT,
                offset=self.TEST_OFFSET_ZERO,
            )
        )

        self.assertEqual(
            len(self.applications_received_by_personal_profile), list_view.total_count
        )

        for i in range(len(list_view.items)):
            application = self.applications_received_by_personal_profile[
                i
            ].adoption_application_data
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
                    application.state,
                    application.application_date,
                    application.open_space,
                    application.safety_in_open_spaces,
                    application.animal_nice_to_others,
                ),
                (
                    list_view.items[i].entity_id,
                    list_view.items[i].ever_had_pet,
                    list_view.items[i].has_pet,
                    list_view.items[i].type_of_housing,
                    list_view.items[i].pet_time_commitment,
                    list_view.items[i].adoption_info,
                    list_view.items[i].adopter_profile_id,
                    list_view.items[i].animal_id,
                    list_view.items[i].state,
                    list_view.items[i].application_date,
                    list_view.items[i].open_space,
                    list_view.items[i].safety_in_open_spaces,
                    list_view.items[i].animal_nice_to_others,
                ),
            )

    async def test_get_all_received_adoption_applications_by_organization_success(
        self,
    ) -> None:
        list_view: AdoptionApplicationListView = await self.use_case.execute(
            GetAdoptionApplicationsUseCase.Request(
                account_id=self.collaborator_profile.profile_data.account_id,
                filter_by_sent_applications=False,
                limit=self.TEST_NO_LIMIT,
                offset=self.TEST_OFFSET_ZERO,
            )
        )

        self.assertEqual(
            len(self.applications_received_by_organization), list_view.total_count
        )

        for i in range(len(list_view.items)):
            application = self.applications_received_by_organization[
                i
            ].adoption_application_data
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
                    application.state,
                    application.application_date,
                    application.open_space,
                    application.safety_in_open_spaces,
                    application.animal_nice_to_others,
                ),
                (
                    list_view.items[i].entity_id,
                    list_view.items[i].ever_had_pet,
                    list_view.items[i].has_pet,
                    list_view.items[i].type_of_housing,
                    list_view.items[i].pet_time_commitment,
                    list_view.items[i].adoption_info,
                    list_view.items[i].adopter_profile_id,
                    list_view.items[i].animal_id,
                    list_view.items[i].state,
                    list_view.items[i].application_date,
                    list_view.items[i].open_space,
                    list_view.items[i].safety_in_open_spaces,
                    list_view.items[i].animal_nice_to_others,
                ),
            )
