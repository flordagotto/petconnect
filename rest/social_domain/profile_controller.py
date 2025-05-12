from dataclasses import dataclass
from datetime import date
from typing import Union

from bounded_contexts.auth.value_objects import TokenData
from bounded_contexts.social_domain.services.profile_service import ModifyProfileData
from bounded_contexts.social_domain.use_cases import (
    GetProfileUseCase,
    GetOrganizationProfilesUseCase,
    EditOrganizationMemberStatus,
    EditPersonalProfileUseCase,
)
from bounded_contexts.social_domain.views.profile_views import (
    BaseProfileView,
    PersonalProfileView,
    OrganizationalProfileView,
    PaginationFriendlyOrganizationalProfileView,
)
from infrastructure.rest import BaseAPIController, TokenDependency


class ProfileController(BaseAPIController):
    async def get(self, account_id: str) -> BaseProfileView:
        get_profile: GetProfileUseCase = self.dependencies.resolve(GetProfileUseCase)

        return await get_profile.execute(
            GetProfileUseCase.Request(account_id=account_id)
        )

    async def index_organizational_profiles(
        self, token: TokenDependency
    ) -> PaginationFriendlyOrganizationalProfileView:
        token_data: TokenData = await self._get_token_data(token=token)

        get_organization_profiles: GetOrganizationProfilesUseCase = (
            self.dependencies.resolve(GetOrganizationProfilesUseCase)
        )

        return await get_organization_profiles.execute(
            GetOrganizationProfilesUseCase.Request(
                actor_account_id=token_data.account_id
            )
        )

    async def put_organization_member_status(
        self, token: TokenDependency, member_account_id: str, accepted: bool
    ) -> None:
        token_data: TokenData = await self._get_token_data(token=token)

        edit_organization_member_status: EditOrganizationMemberStatus = (
            self.dependencies.resolve(EditOrganizationMemberStatus)
        )

        await edit_organization_member_status.execute(
            EditOrganizationMemberStatus.Request(
                actor_account_id=token_data.account_id,
                member_account_id=member_account_id,
                accepted=accepted,
            )
        )

    @dataclass
    class ModifyProfileData:
        entity_id: str
        first_name: str
        surname: str
        phone_number: str
        government_id: str
        birthdate: date
        social_media_url: str | None = None

    async def put_personal_profile(
        self, token: TokenDependency, request: ModifyProfileData
    ) -> None:
        token_data: TokenData = await self._get_token_data(token=token)

        edit_personal_profile_use_case: EditPersonalProfileUseCase = (
            self.dependencies.resolve(EditPersonalProfileUseCase)
        )

        await edit_personal_profile_use_case.execute(
            EditPersonalProfileUseCase.Request(
                account_id=token_data.account_id,
                profile_data=ModifyProfileData(
                    entity_id=request.entity_id,
                    first_name=request.first_name,
                    surname=request.surname,
                    phone_number=request.phone_number,
                    government_id=request.government_id,
                    birthdate=request.birthdate,
                    social_media_url=request.social_media_url,
                ),
            )
        )

    def register_routes(self) -> None:
        PREFIX: str = "/social/profile"

        self._register_get_route(
            f"{PREFIX}",
            method=self.get,
            response_model=Union[OrganizationalProfileView, PersonalProfileView],
        )

        self._register_get_route(
            f"{PREFIX}/organization-profiles",
            method=self.index_organizational_profiles,
        )

        self._register_put_route(
            f"{PREFIX}/organization-profiles/status",
            method=self.put_organization_member_status,
        )

        self._register_put_route(
            f"{PREFIX}/personal-profile",
            method=self.put_personal_profile,
        )
