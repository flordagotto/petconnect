from datetime import date
from typing import cast, Sequence

from pydantic import BaseModel
from bounded_contexts.social_domain.entities import (
    PersonalProfile,
    OrganizationalProfile,
    BaseProfile,
)
from bounded_contexts.social_domain.enum import ProfileTypes


class BaseProfileView(BaseModel):
    account_id: str
    profile_id: str
    entity_id: str
    first_name: str
    surname: str
    phone_number: str
    profile_type: str
    birthdate: date
    government_id: str
    email: str


class PersonalProfileView(BaseProfileView):
    social_media_url: str | None = None


class OrganizationalProfileView(BaseProfileView):
    organization_id: str
    organization_role: str
    verified_by_organization: bool


class PaginationFriendlyOrganizationalProfileView(BaseModel):
    items: Sequence[OrganizationalProfileView]
    total_count: int


class ProfileViewFactory:
    @staticmethod
    def create_personal_profile_view(profile: PersonalProfile) -> PersonalProfileView:
        return PersonalProfileView(
            account_id=profile.account.entity_id,
            profile_id=profile.entity_id,
            entity_id=profile.entity_id,
            first_name=profile.first_name,
            surname=profile.surname,
            phone_number=profile.phone_number,
            profile_type=profile.profile_type.value,
            birthdate=profile.birthdate,
            government_id=profile.government_id,
            email=profile.account.email,
            social_media_url=profile.social_media_url,
        )

    @staticmethod
    def create_organizational_profile_view(
        profile: OrganizationalProfile,
    ) -> OrganizationalProfileView:
        return OrganizationalProfileView(
            account_id=profile.account.entity_id,
            profile_id=profile.entity_id,
            entity_id=profile.entity_id,
            first_name=profile.first_name,
            surname=profile.surname,
            phone_number=profile.phone_number,
            profile_type=profile.profile_type.value,
            organization_id=profile.organization_id,
            organization_role=profile.organization_role.value,
            birthdate=profile.birthdate,
            government_id=profile.government_id,
            verified_by_organization=profile.verified_by_organization,
            email=profile.account.email,
        )

    @staticmethod
    def create_profile_view(profile: BaseProfile) -> BaseProfileView:
        if profile.profile_type == ProfileTypes.ORGANIZATIONAL_PROFILE:
            organization_profile: OrganizationalProfile = cast(
                OrganizationalProfile, profile
            )

            return ProfileViewFactory.create_organizational_profile_view(
                profile=organization_profile
            )

        personal_profile: PersonalProfile = cast(PersonalProfile, profile)

        return ProfileViewFactory.create_personal_profile_view(profile=personal_profile)

    @staticmethod
    def create_multiple_organizational_profiles_view(
        organization_profiles: Sequence[OrganizationalProfile],
    ) -> list[OrganizationalProfileView]:
        return [
            ProfileViewFactory.create_organizational_profile_view(profile=profile)
            for profile in organization_profiles
        ]
