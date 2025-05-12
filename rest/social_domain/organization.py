from datetime import date

from pydantic import BaseModel

from bounded_contexts.auth.value_objects import TokenData
from bounded_contexts.social_domain.use_cases import (
    CreateOrganizationUseCase,
    GetOrganizationsUseCase,
    GetOrganizationUseCase,
    VerifyOrganizationUseCase,
)
from bounded_contexts.social_domain.views import OrganizationView, OrganizationListView
from infrastructure.rest import BaseAPIController, TokenDependency


class OrganizationController(BaseAPIController):
    class CreateOrganizationRequest(BaseModel):
        class OrgAdminProfileRequest(BaseModel):
            email: str
            password: str
            first_name: str
            surname: str
            phone_number: str
            government_id: str
            birthdate: date

        organization_admin_profile: OrgAdminProfileRequest
        organization_name: str
        social_media_url: str | None = None

    async def post(self, body: CreateOrganizationRequest) -> OrganizationView:
        create_organization_use_case: CreateOrganizationUseCase = (
            self.dependencies.resolve(CreateOrganizationUseCase)
        )

        return await create_organization_use_case.execute(
            CreateOrganizationUseCase.Request(
                organization_admin_request=CreateOrganizationUseCase.Request.OrganizationAdminRequest(
                    email=body.organization_admin_profile.email,
                    password=body.organization_admin_profile.password,
                    first_name=body.organization_admin_profile.first_name,
                    surname=body.organization_admin_profile.surname,
                    phone_number=body.organization_admin_profile.phone_number,
                    government_id=body.organization_admin_profile.government_id,
                    birthdate=body.organization_admin_profile.birthdate,
                ),
                organization_request=CreateOrganizationUseCase.Request.OrganizationRequest(
                    organization_name=body.organization_name,
                    phone_number=body.organization_admin_profile.phone_number,
                    social_media_url=body.social_media_url,
                ),
            )
        )

    async def get(self, entity_id: str) -> OrganizationView:
        get_organization_use_case: GetOrganizationUseCase = self.dependencies.resolve(
            GetOrganizationUseCase
        )

        organization_view = await get_organization_use_case.execute(entity_id=entity_id)
        return organization_view

    async def index_organizations(
        self, limit: int | None = None, offset: int | None = 0
    ) -> OrganizationListView:
        get_organizations_use_case: GetOrganizationsUseCase = self.dependencies.resolve(
            GetOrganizationsUseCase
        )

        org_view = await get_organizations_use_case.execute(
            GetOrganizationsUseCase.Request(limit=limit, offset=offset)
        )
        return org_view

    async def post_verify(self, token: TokenDependency, organization_id: str) -> None:
        token_data: TokenData = await self._get_token_data(token=token)

        verify_organization = self.dependencies.resolve(VerifyOrganizationUseCase)

        await verify_organization.execute(
            actor_account_id=token_data.account_id,
            organization_id=organization_id,
        )

    def register_routes(self) -> None:
        PREFIX: str = "/social/organization"

        self._register_post_route(f"{PREFIX}", method=self.post)
        self._register_get_route(f"{PREFIX}/all", method=self.index_organizations)
        self._register_get_route(f"{PREFIX}", method=self.get)
        self._register_get_route(f"{PREFIX}/verify", method=self.post_verify)
