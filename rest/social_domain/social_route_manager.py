from infrastructure.rest import BaseAPIController
from rest import RouteManager
from rest.social_domain import (
    OrganizationController,
    CreateProfileController,
    ProfileController,
)


class SocialRouteManager(RouteManager):
    def _create_controllers(self) -> list[BaseAPIController]:
        create_personal_profile_controller: CreateProfileController = (
            CreateProfileController(
                dependencies=self.dependencies,
            )
        )

        organization_controller: OrganizationController = OrganizationController(
            dependencies=self.dependencies
        )

        profile_controller: ProfileController = ProfileController(
            dependencies=self.dependencies
        )

        return [
            create_personal_profile_controller,
            organization_controller,
            profile_controller,
        ]
