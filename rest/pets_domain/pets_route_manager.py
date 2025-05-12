from infrastructure.rest import BaseAPIController
from rest import RouteManager
from rest.pets_domain.pet import PetController
from rest.pets_domain.pet_sight import PetSightController


class PetsRouteManager(RouteManager):
    def _create_controllers(self) -> list[BaseAPIController]:
        create_pet_controller: PetController = PetController(
            dependencies=self.dependencies,
        )

        create_pet_sight_controller: PetSightController = PetSightController(
            dependencies=self.dependencies,
        )

        return [create_pet_controller, create_pet_sight_controller]
