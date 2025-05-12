from datetime import datetime
from typing import Sequence, Dict
from pydantic import BaseModel

from bounded_contexts.adoptions_domain.entities import AdoptionApplication
from bounded_contexts.adoptions_domain.enum import (
    AdoptionApplicationStates,
    HousingTypes,
    OpenSpacesTypes,
)
from bounded_contexts.adoptions_domain.views import AdoptionAnimalView
from bounded_contexts.social_domain.views.profile_views import BaseProfileView


class AdoptionApplicationView(BaseModel):
    entity_id: str
    application_date: datetime
    ever_had_pet: bool
    has_pet: bool
    type_of_housing: HousingTypes
    pet_time_commitment: str
    adoption_info: str
    adopter_profile_id: str
    animal_id: str
    state: AdoptionApplicationStates
    animal_name: str
    profile_view: BaseProfileView | None = None
    open_space: OpenSpacesTypes | None = None
    safety_in_open_spaces: str | None = None
    animal_nice_to_others: str | None = None


class AdoptionApplicationListView(BaseModel):
    items: Sequence[AdoptionApplicationView]
    total_count: int


class AdoptionApplicationExtraInfoView(BaseModel):
    profile_info: BaseProfileView
    animal_info: AdoptionAnimalView


class AdoptionApplicationViewFactory:
    @staticmethod
    def create_adoption_application_view(
        application: AdoptionApplication,
        animal_name: str,
        profile_view: BaseProfileView | None = None,
    ) -> AdoptionApplicationView:
        return AdoptionApplicationView(
            entity_id=application.entity_id,
            application_date=application.application_date,
            ever_had_pet=application.ever_had_pet,
            has_pet=application.has_pet,
            type_of_housing=application.type_of_housing,
            open_space=application.open_space,
            pet_time_commitment=application.pet_time_commitment,
            adoption_info=application.adoption_info,
            adopter_profile_id=application.adopter_profile_id,
            animal_id=application.animal_id,
            state=application.state,
            animal_name=animal_name,
            profile_view=profile_view,
            safety_in_open_spaces=application.safety_in_open_spaces,
            animal_nice_to_others=application.animal_nice_to_others,
        )

    @staticmethod
    def create_adoption_application_list_view(
        applications: Dict[AdoptionApplication, AdoptionApplicationExtraInfoView],
        total_count: int,
    ) -> AdoptionApplicationListView:
        adoption_applications_list_view: list[AdoptionApplicationView] = []

        for application, extraInfo in applications.items():
            adoption_applications_list_view.append(
                AdoptionApplicationViewFactory.create_adoption_application_view(
                    application=application,
                    animal_name=extraInfo.animal_info.animal_name,
                    profile_view=extraInfo.profile_info,
                )
            )
        return AdoptionApplicationListView(
            items=adoption_applications_list_view, total_count=total_count
        )
