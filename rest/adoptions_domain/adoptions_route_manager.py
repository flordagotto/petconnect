from infrastructure.rest import BaseAPIController
from rest import RouteManager
from rest.adoptions_domain import AdoptionAnimalController
from rest.adoptions_domain.adoption_application import AdoptionApplicationController


class AdoptionsRouteManager(RouteManager):
    def _create_controllers(self) -> list[BaseAPIController]:
        adoption_animal_controller: AdoptionAnimalController = AdoptionAnimalController(
            dependencies=self.dependencies,
        )

        adoption_application_controller: AdoptionApplicationController = (
            AdoptionApplicationController(
                dependencies=self.dependencies,
            )
        )

        return [adoption_animal_controller, adoption_application_controller]
