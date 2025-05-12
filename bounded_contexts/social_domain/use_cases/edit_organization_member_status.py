from dataclasses import dataclass
from bounded_contexts.social_domain.entities import OrganizationalProfile
from bounded_contexts.social_domain.use_cases import BaseSocialUseCase
from infrastructure.uow_abstraction import unit_of_work, UnitOfWork


class EditOrganizationMemberStatus(BaseSocialUseCase):
    @dataclass
    class Request:
        actor_account_id: str
        member_account_id: str
        accepted: bool

    @unit_of_work
    async def execute(self, request: Request, uow: UnitOfWork) -> None:
        actor_profile: OrganizationalProfile = (
            await self.profile_service.get_organizational_profile_by_account_id(
                uow=uow,
                account_id=request.actor_account_id,
            )
        )

        profile: OrganizationalProfile = (
            await self.profile_service.get_organizational_profile_by_account_id(
                uow=uow,
                account_id=request.member_account_id,
            )
        )

        if request.accepted:
            await self.organization_service.accept_organization_profile(
                actor_profile=actor_profile,
                profile=profile,
            )

        else:
            await self.organization_service.disable_organization_profile(
                actor_profile=actor_profile, profile=profile
            )
