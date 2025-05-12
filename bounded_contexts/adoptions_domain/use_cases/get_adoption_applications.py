from dataclasses import dataclass
from typing import Sequence, Dict, cast

from bounded_contexts.adoptions_domain.entities import AdoptionApplication
from bounded_contexts.adoptions_domain.services import AdoptionAnimalsService
from bounded_contexts.adoptions_domain.services.adoption_applications_service import (
    AdoptionApplicationService,
)
from bounded_contexts.adoptions_domain.views.adoption_animal_views import (
    AdoptionAnimalViewFactory,
    AdoptionAnimalView,
)
from bounded_contexts.adoptions_domain.views.adoption_application_views import (
    AdoptionApplicationViewFactory,
    AdoptionApplicationListView,
    AdoptionApplicationExtraInfoView,
)
from bounded_contexts.social_domain.entities import BaseProfile, OrganizationalProfile
from bounded_contexts.social_domain.enum import ProfileTypes
from bounded_contexts.social_domain.services.organization_service import (
    OrganizationService,
)
from bounded_contexts.social_domain.services.profile_service import ProfileService
from bounded_contexts.social_domain.views import ProfileViewFactory
from bounded_contexts.social_domain.views.profile_views import BaseProfileView
from common.use_case import BaseUseCase
from infrastructure.database import RepositoryUtils
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class GetAdoptionApplicationsUseCase(BaseUseCase):
    @dataclass
    class Request:
        account_id: str
        filter_by_sent_applications: bool
        limit: int | None
        offset: int | None

    def __init__(
        self,
        repository_utils: RepositoryUtils,
        adoption_application_service: AdoptionApplicationService,
        adoption_animals_service: AdoptionAnimalsService,
        adoption_application_view_factory: AdoptionApplicationViewFactory,
        profile_view_factory: ProfileViewFactory,
        animal_view_factory: AdoptionAnimalViewFactory,
        profile_service: ProfileService,
        organization_service: OrganizationService,
    ) -> None:
        super().__init__(
            repository_utils=repository_utils,
        )

        self.adoption_application_service = adoption_application_service
        self.adoption_animals_service = adoption_animals_service
        self.adoption_application_view_factory = adoption_application_view_factory
        self.profile_view_factory = profile_view_factory
        self.animal_view_factory = animal_view_factory
        self.profile_service = profile_service
        self.organization_service = organization_service

    @unit_of_work
    async def execute(
        self, request: Request, uow: UnitOfWork
    ) -> AdoptionApplicationListView:
        actor_profile: BaseProfile = (
            await self.profile_service.get_profile_by_account_id(
                uow=uow, account_id=request.account_id
            )
        )

        applications: Sequence[
            AdoptionApplication
        ] = await self.adoption_application_service.get_all_applications(
            uow=uow,
            profile=actor_profile,
            filter_by_sent_applications=request.filter_by_sent_applications,
            limit=request.limit,
            offset=request.offset,
        )

        total_count: int = (
            await self.adoption_application_service.get_all_applications_count(
                uow=uow,
                profile=actor_profile,
                filter_by_sent_applications=request.filter_by_sent_applications,
            )
        )

        if request.filter_by_sent_applications:
            return self.adoption_application_view_factory.create_adoption_application_list_view(
                applications=await self.get_extra_info_for_sent_applications(
                    uow=uow,
                    applications=applications,
                    publicator_name=actor_profile.first_name,
                ),
                total_count=total_count,
            )
        else:
            return self.adoption_application_view_factory.create_adoption_application_list_view(
                applications=await self.get_extra_info_for_received_applications(
                    uow=uow,
                    applications=applications,
                ),
                total_count=total_count,
            )

    async def get_extra_info_for_sent_applications(
        self,
        uow: UnitOfWork,
        applications: Sequence[AdoptionApplication],
        publicator_name: str,
    ) -> Dict[AdoptionApplication, AdoptionApplicationExtraInfoView]:
        adoption_application_dict = {}
        for application in applications:
            adoption_animal = (
                await self.adoption_animals_service.get_adoption_animal_by_id(
                    uow=uow, entity_id=application.animal_id, get_all=True
                )
            )
            animal_view: AdoptionAnimalView = (
                self.animal_view_factory.create_adoption_animal_view(
                    adoption_animal=adoption_animal, publicator_name=publicator_name
                )
            )

            adoption_giver_profile = await self.profile_service.get_profile(
                uow=uow, entity_id=adoption_animal.profile_id
            )
            profile_view: BaseProfileView = (
                self.profile_view_factory.create_profile_view(adoption_giver_profile)
            )

            if profile_view.profile_type == ProfileTypes.ORGANIZATIONAL_PROFILE.value:
                organizational_profile: OrganizationalProfile = cast(
                    OrganizationalProfile, adoption_giver_profile
                )
                organization = await self.organization_service.get_organization_by_id(
                    uow=uow, entity_id=organizational_profile.organization_id
                )

                profile_view.first_name = organization.organization_name
                profile_view.surname = ""

            extra_info = AdoptionApplicationExtraInfoView(
                profile_info=profile_view, animal_info=animal_view
            )

            adoption_application_dict[application] = extra_info
        return adoption_application_dict

    async def get_extra_info_for_received_applications(
        self, uow: UnitOfWork, applications: Sequence[AdoptionApplication]
    ) -> Dict[AdoptionApplication, AdoptionApplicationExtraInfoView]:
        adoption_application_dict = {}
        for application in applications:
            adopter_profile = await self.profile_service.get_profile(
                uow=uow, entity_id=application.adopter_profile_id
            )
            profile_view: BaseProfileView = (
                self.profile_view_factory.create_profile_view(adopter_profile)
            )

            adoption_animal = (
                await self.adoption_animals_service.get_adoption_animal_by_id(
                    uow=uow, entity_id=application.animal_id, get_all=True
                )
            )
            animal_view: AdoptionAnimalView = (
                self.animal_view_factory.create_adoption_animal_view(
                    adoption_animal=adoption_animal,
                    publicator_name=profile_view.first_name,
                )
            )

            extra_info = AdoptionApplicationExtraInfoView(
                profile_info=profile_view, animal_info=animal_view
            )

            adoption_application_dict[application] = extra_info
        return adoption_application_dict
