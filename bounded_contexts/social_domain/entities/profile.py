from abc import ABC
from datetime import date

from bounded_contexts.auth.entities import Account
from bounded_contexts.social_domain.enum import OrganizationRoles, ProfileTypes
from common.entities import BaseDomainEntity


class BaseProfile(BaseDomainEntity, ABC):
    def __init__(
        self,
        entity_id: str,
        first_name: str,
        surname: str,
        phone_number: str,
        account: Account,
        profile_type: ProfileTypes,
        government_id: str,
        birthdate: date,
    ) -> None:
        super().__init__(entity_id=entity_id)

        self.first_name = first_name
        self.surname = surname
        self.phone_number = phone_number
        self.account = account
        self.profile_type = profile_type
        self.government_id = government_id
        self.birthdate = birthdate

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.surname}"


class PersonalProfile(BaseProfile):
    def __init__(
        self,
        entity_id: str,
        first_name: str,
        surname: str,
        phone_number: str,
        account: Account,
        government_id: str,
        birthdate: date,
        social_media_url: str | None = None,
    ) -> None:
        super().__init__(
            entity_id=entity_id,
            first_name=first_name,
            surname=surname,
            phone_number=phone_number,
            account=account,
            profile_type=ProfileTypes.PERSONAL_PROFILE,
            government_id=government_id,
            birthdate=birthdate,
        )
        self.social_media_url = social_media_url


class OrganizationalProfile(BaseProfile):
    def __init__(
        self,
        entity_id: str,
        first_name: str,
        surname: str,
        phone_number: str,
        account: Account,
        organization_id: str,
        organization_role: OrganizationRoles,
        government_id: str,
        birthdate: date,
        verified_by_organization: bool,
    ) -> None:
        super().__init__(
            entity_id=entity_id,
            first_name=first_name,
            surname=surname,
            phone_number=phone_number,
            account=account,
            profile_type=ProfileTypes.ORGANIZATIONAL_PROFILE,
            government_id=government_id,
            birthdate=birthdate,
        )

        self.organization_id = organization_id
        self.organization_role = organization_role
        self.verified_by_organization = verified_by_organization
