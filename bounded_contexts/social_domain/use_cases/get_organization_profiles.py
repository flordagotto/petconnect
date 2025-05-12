from dataclasses import dataclass
from typing import Sequence

from bounded_contexts.social_domain.entities import OrganizationalProfile
from bounded_contexts.social_domain.use_cases import BaseSocialUseCase
from bounded_contexts.social_domain.views import (
    PaginationFriendlyOrganizationalProfileView,
)
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class GetOrganizationProfilesUseCase(BaseSocialUseCase):
    @dataclass
    class Request:
        actor_account_id: str
        offset: int | None = None
        limit: int | None = None

    @unit_of_work
    async def execute(
        self, request: Request, uow: UnitOfWork
    ) -> PaginationFriendlyOrganizationalProfileView:
        actor_profile: OrganizationalProfile = (
            await self.profile_service.get_organizational_profile_by_account_id(
                uow=uow, account_id=request.actor_account_id
            )
        )

        organization_profiles: Sequence[
            OrganizationalProfile
        ] = await self.profile_service.get_organization_profiles(
            uow=uow,
            actor_profile=actor_profile,
            offset=request.offset,
            limit=request.limit,
        )

        total_count: int = await self.profile_service.get_organization_profiles_count(
            uow=uow,
            actor_profile=actor_profile,
        )

        views = self.profile_view_factory.create_multiple_organizational_profiles_view(
            organization_profiles=organization_profiles,
        )

        return PaginationFriendlyOrganizationalProfileView(
            items=views,
            total_count=total_count,
        )
