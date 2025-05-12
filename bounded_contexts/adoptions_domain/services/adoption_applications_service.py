from dataclasses import dataclass
from datetime import datetime
from typing import Sequence, cast
from uuid import uuid4

from bounded_contexts.adoptions_domain.entities import (
    AdoptionApplication,
    AdoptionAnimal,
)
from bounded_contexts.adoptions_domain.entities.adoption import Adoption
from bounded_contexts.adoptions_domain.enum import (
    HousingTypes,
    AdoptionApplicationStates,
    OpenSpacesTypes,
    AdoptionAnimalStates,
)
from bounded_contexts.adoptions_domain.events import ApplicationStateUpdatedEvent
from bounded_contexts.adoptions_domain.events.adoption_events_handler import (
    AnimalAdoptedEvent,
)
from bounded_contexts.adoptions_domain.exceptions import (
    ApplicationNotFoundByIdException,
    ApplicationNotFoundByAnimalIdException,
    ApplicationByOrganizationNotValidException,
    AdoptionAnimalApplicationUnauthorizedAccessException,
    AnimalAlreadyAdoptedException,
    AdoptionApplicationAlreadyClosedException,
    AdoptionApplicationForOwnAnimalException,
    ProfileAlreadyAppliedException,
)
from bounded_contexts.adoptions_domain.repositories import (
    AdoptionApplicationsRepository,
    AdoptionAnimalsRepository,
)
from bounded_contexts.adoptions_domain.repositories.adoptions_repository import (
    AdoptionsRepository,
)
from bounded_contexts.social_domain.entities import (
    BaseProfile,
    OrganizationalProfile,
)
from bounded_contexts.social_domain.enum import ProfileTypes
from infrastructure.date_utils import float_timestamp, datetime_now_tz
from infrastructure.uow_abstraction import UnitOfWork


@dataclass
class AdoptionApplicationData:
    entity_id: str
    ever_had_pet: bool
    has_pet: bool
    type_of_housing: HousingTypes
    pet_time_commitment: str
    adoption_info: str
    adopter_profile_id: str
    animal_id: str
    state: AdoptionApplicationStates
    application_date: datetime
    open_space: OpenSpacesTypes | None = None
    safety_in_open_spaces: str | None = None
    animal_nice_to_others: str | None = None


@dataclass
class ModifyAdoptionApplicationData:
    entity_id: str
    state: AdoptionApplicationStates


class AdoptionApplicationService:
    def __init__(
        self,
        applications_repository: AdoptionApplicationsRepository,
        adoptions_repository: AdoptionsRepository,
        animals_repository: AdoptionAnimalsRepository,
    ) -> None:
        self.applications_repository = applications_repository
        self.adoptions_repository = adoptions_repository
        self.animals_repository = animals_repository

    async def create_application(
        self,
        uow: UnitOfWork,
        adopter_profile: BaseProfile,
        animal: AdoptionAnimal,
        ever_had_pet: bool,
        has_pet: bool,
        type_of_housing: HousingTypes,
        pet_time_commitment: str,
        adoption_info: str,
        open_space: OpenSpacesTypes | None,
        safety_in_open_spaces: str | None,
        animal_nice_to_others: str | None,
    ) -> AdoptionApplication:
        self.__assert_adopter_is_personal_profile(adopter_profile=adopter_profile)
        self.__assert_application_is_for_foreign_animal(adopter_profile, animal=animal)
        self.__assert_animal_already_adopted(animal=animal)
        await self.__assert_profile_has_not_applied(
            uow=uow, adopter_profile=adopter_profile, animal=animal
        )

        application_id: str = uuid4().hex

        application: AdoptionApplication = AdoptionApplication(
            entity_id=application_id,
            ever_had_pet=ever_had_pet,
            has_pet=has_pet,
            type_of_housing=type_of_housing,
            open_space=open_space,
            pet_time_commitment=pet_time_commitment,
            adoption_info=adoption_info,
            adopter_profile_id=adopter_profile.entity_id,
            animal_id=animal.entity_id,
            safety_in_open_spaces=safety_in_open_spaces,
            animal_nice_to_others=animal_nice_to_others,
        )

        await self.applications_repository.add_application(
            session=uow.session, application=application
        )

        return application

    async def get_application_by_id(
        self, uow: UnitOfWork, entity_id: str
    ) -> AdoptionApplication:
        adoption_application: AdoptionApplication | None = (
            await self.applications_repository.get_application_by_id(
                session=uow.session, entity_id=entity_id
            )
        )

        if not adoption_application:
            raise ApplicationNotFoundByIdException(entity_id=entity_id)

        return adoption_application

    async def get_application_by_animal_id(
        self, uow: UnitOfWork, adoption_animal_id: str
    ) -> AdoptionApplication:
        adoption_application: AdoptionApplication | None = (
            await self.applications_repository.get_application_by_animal_id(
                session=uow.session, adoption_animal_id=adoption_animal_id
            )
        )

        if not adoption_application:
            raise ApplicationNotFoundByAnimalIdException(animal_id=adoption_animal_id)

        return adoption_application

    async def get_applications_by_animal_id(
        self, uow: UnitOfWork, adoption_animal_id: str
    ) -> Sequence[AdoptionApplication]:
        adoption_applications: Sequence[
            AdoptionApplication
        ] = await self.applications_repository.get_received_applications_by_animal_id(
            session=uow.session, adoption_animal_id=adoption_animal_id
        )

        return adoption_applications

    async def get_all_applications(
        self,
        uow: UnitOfWork,
        profile: BaseProfile,
        filter_by_sent_applications: bool,
        limit: int | None = None,
        offset: int | None = 0,
    ) -> Sequence[AdoptionApplication]:
        if filter_by_sent_applications:
            if profile.profile_type == ProfileTypes.ORGANIZATIONAL_PROFILE:
                return []
            return await self.applications_repository.get_sent_applications(
                session=uow.session,
                profile_id=profile.entity_id,
                limit=limit,
                offset=offset,
            )
        else:
            if profile.profile_type == ProfileTypes.PERSONAL_PROFILE:
                return await self.applications_repository.get_received_applications_by_personal_profile(
                    session=uow.session,
                    profile_id=profile.entity_id,
                    limit=limit,
                    offset=offset,
                )
            else:
                organizational_profile = cast(OrganizationalProfile, profile)
                return await self.applications_repository.get_received_applications_by_organizational_profile(
                    session=uow.session,
                    organization_id=organizational_profile.organization_id,
                    limit=limit,
                    offset=offset,
                )

    # TODO: check these nested ifs

    async def get_all_applications_count(
        self,
        uow: UnitOfWork,
        profile: BaseProfile,
        filter_by_sent_applications: bool,
    ) -> int:
        if filter_by_sent_applications:
            if profile.profile_type == ProfileTypes.ORGANIZATIONAL_PROFILE:
                return 0
            return await self.applications_repository.count_sent_applications(
                session=uow.session, profile_id=profile.entity_id
            )
        else:
            if profile.profile_type == ProfileTypes.PERSONAL_PROFILE:
                return await self.applications_repository.count_received_applications_by_personal_profile(
                    session=uow.session, profile_id=profile.entity_id
                )
            else:
                organizational_profile = cast(OrganizationalProfile, profile)
                return await self.applications_repository.count_received_applications_by_organizational_profile(
                    session=uow.session,
                    organization_id=organizational_profile.organization_id,
                )

    async def edit_application(
        self,
        uow: UnitOfWork,
        actor_profile: BaseProfile,
        animal: AdoptionAnimal,
        application: AdoptionApplication,
        application_new_data: ModifyAdoptionApplicationData,
        adopter_profile: BaseProfile,
    ) -> None:
        self.__assert_animal_already_adopted(animal=animal)
        self.__assert_application_already_closed(application=application)

        if actor_profile.profile_type == ProfileTypes.PERSONAL_PROFILE:
            self.__assert_profile_is_owner(profile=actor_profile, animal=animal)
        else:
            organizational_profile = cast(OrganizationalProfile, actor_profile)
            self.__assert_organization_is_owner(
                profile=organizational_profile, animal=animal
            )

        application.state = application_new_data.state

        if application_new_data.state == AdoptionApplicationStates.ACCEPTED:
            await self.accept_adoption_application(
                uow=uow,
                animal=animal,
                application=application,
                adopter_profile=adopter_profile,
            )

        await uow.flush()

        self.__issue_adoption_application_state_updated_event(
            uow=uow,
            profile=actor_profile,
            adoption_application_id=application.entity_id,
        )

    async def accept_adoption_application(
        self,
        uow: UnitOfWork,
        animal: AdoptionAnimal,
        application: AdoptionApplication,
        adopter_profile: BaseProfile,
    ):
        adoption_id: str = uuid4().hex

        adoption: Adoption = Adoption(
            entity_id=adoption_id,
            adoption_date=datetime_now_tz(),
            adoption_application_id=application.entity_id,
        )

        await self.adoptions_repository.add_adoption(
            session=uow.session, adoption=adoption
        )

        animal.state = AdoptionAnimalStates.ADOPTED

        await self.reject_other_applications(uow=uow, accepted_application=application)

        self.__issue_animal_adopted_event(
            uow=uow,
            actor_account_id=adopter_profile.account.entity_id,
            animal_id=application.animal_id,
        )

    async def reject_other_applications(
        self, uow: UnitOfWork, accepted_application: AdoptionApplication
    ):
        pending_applications: Sequence[
            AdoptionApplication
        ] = await self.get_applications_by_animal_id(
            uow=uow, adoption_animal_id=accepted_application.animal_id
        )

        applications_to_remove = [
            application
            for application in pending_applications
            if application.entity_id != accepted_application.entity_id
        ]

        await self.reject_applications(applications_to_remove)

    @staticmethod
    async def reject_applications(
        applications_to_delete: Sequence[AdoptionApplication],
    ):
        for i in range(len(applications_to_delete)):
            applications_to_delete[i].state = AdoptionApplicationStates.REJECTED

    async def delete_application(
        self,
        uow: UnitOfWork,
        actor_profile: BaseProfile,
        animal: AdoptionAnimal,
        application: AdoptionApplication,
    ) -> None:
        self.__assert_profile_is_owner(profile=actor_profile, animal=animal)
        await self.applications_repository.delete_applications(
            session=uow.session, application=application
        )

    @staticmethod
    def __assert_adopter_is_personal_profile(adopter_profile: BaseProfile) -> None:
        if adopter_profile.profile_type != ProfileTypes.PERSONAL_PROFILE:
            raise ApplicationByOrganizationNotValidException(
                actor_account_id=adopter_profile.entity_id
            )

    @staticmethod
    def __assert_profile_is_owner(profile: BaseProfile, animal: AdoptionAnimal) -> None:
        if animal.profile_id != profile.entity_id:
            raise AdoptionAnimalApplicationUnauthorizedAccessException(
                actor_account_id=profile.account.entity_id, animal_id=animal.entity_id
            )

    @staticmethod
    def __assert_organization_is_owner(
        profile: OrganizationalProfile, animal: AdoptionAnimal
    ) -> None:
        if animal.organization_id != profile.organization_id:
            raise AdoptionAnimalApplicationUnauthorizedAccessException(
                actor_account_id=profile.account.entity_id, animal_id=animal.entity_id
            )

    @staticmethod
    def __assert_animal_already_adopted(animal: AdoptionAnimal) -> None:
        if animal.state == AdoptionAnimalStates.ADOPTED:
            raise AnimalAlreadyAdoptedException(animal_id=animal.entity_id)

    @staticmethod
    def __assert_application_already_closed(application: AdoptionApplication) -> None:
        if application.state != AdoptionApplicationStates.PENDING:
            raise AdoptionApplicationAlreadyClosedException(
                adoption_application_id=application.entity_id
            )

    @staticmethod
    def __assert_application_is_for_foreign_animal(
        profile: BaseProfile, animal: AdoptionAnimal
    ) -> None:
        if profile.entity_id == animal.profile_id:
            raise AdoptionApplicationForOwnAnimalException(
                animal_id=animal.entity_id, actor_account_id=profile.entity_id
            )

    async def __assert_profile_has_not_applied(
        self, uow: UnitOfWork, adopter_profile: BaseProfile, animal: AdoptionAnimal
    ) -> None:
        sent_applications = await self.get_all_applications(
            uow=uow, profile=adopter_profile, filter_by_sent_applications=True
        )
        sent_applications_to_animal = [
            application
            for application in sent_applications
            if application.animal_id == animal.entity_id
        ]

        if sent_applications_to_animal:
            raise ProfileAlreadyAppliedException(
                animal_id=animal.entity_id, actor_account_id=adopter_profile.entity_id
            )

    @staticmethod
    def __issue_animal_adopted_event(
        uow: UnitOfWork,
        actor_account_id: str,
        animal_id: str,
    ) -> None:
        # TODO: Test handlers for this
        uow.emit_event(
            AnimalAdoptedEvent(
                actor_account_id=actor_account_id,
                animal_id=animal_id,
                issued=float_timestamp(),
            )
        )

    @staticmethod
    def __issue_adoption_application_state_updated_event(
        uow: UnitOfWork, profile: BaseProfile, adoption_application_id: str
    ) -> None:
        uow.emit_event(
            ApplicationStateUpdatedEvent(
                actor_account_id=profile.account.entity_id,
                issued=float_timestamp(),
                adoption_application_id=adoption_application_id,
                email=profile.account.email,
            )
        )
