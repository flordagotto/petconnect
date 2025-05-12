from datetime import date

from pydantic import BaseModel
from bounded_contexts.auth.use_cases import CreateAccountUseCase
from bounded_contexts.social_domain.enum import OrganizationRoles
from bounded_contexts.social_domain.use_cases import (
    CreatePersonalProfileUseCase,
    CreateOrganizationalProfileUseCase,
)
from bounded_contexts.social_domain.views import (
    PersonalProfileView,
    OrganizationalProfileView,
)
from infrastructure.rest import BaseAPIController


class CreateProfileController(BaseAPIController):
    class CreatePersonalProfileRequest(BaseModel):
        email: str
        password: str
        first_name: str
        surname: str
        phone_number: str
        birthdate: date
        government_id: str
        social_media_url: str | None = None

    async def post(self, body: CreatePersonalProfileRequest) -> PersonalProfileView:
        create_personal_profile: CreatePersonalProfileUseCase = (
            self.dependencies.resolve(
                CreatePersonalProfileUseCase,
            )
        )

        return await create_personal_profile.execute(
            CreatePersonalProfileUseCase.Request(
                account_request=CreateAccountUseCase.Request(
                    email=body.email,
                    password=body.password,
                ),
                first_name=body.first_name,
                surname=body.surname,
                phone_number=body.phone_number,
                birthdate=body.birthdate,
                government_id=body.government_id,
            )
        )

    class CreateOrganizationalProfileRequest(BaseModel):
        organization_id: str
        email: str
        password: str
        first_name: str
        surname: str
        phone_number: str
        government_id: str
        birthdate: date
        organization_role: OrganizationRoles

    async def post_organizational(
        self, body: CreateOrganizationalProfileRequest
    ) -> OrganizationalProfileView:
        create_organizational_profile: CreateOrganizationalProfileUseCase = (
            self.dependencies.resolve(
                CreateOrganizationalProfileUseCase,
            )
        )

        return await create_organizational_profile.execute(
            CreateOrganizationalProfileUseCase.Request(
                email=body.email,
                password=body.password,
                first_name=body.first_name,
                surname=body.surname,
                phone_number=body.phone_number,
                birthdate=body.birthdate,
                government_id=body.government_id,
                organization_id=body.organization_id,
                organization_role=body.organization_role,
            )
        )

    def register_routes(self) -> None:
        PREFIX: str = "/auth/signup"

        self._register_post_route(f"{PREFIX}", method=self.post)

        self._register_post_route(
            f"{PREFIX}/organizational_profile", method=self.post_organizational
        )
