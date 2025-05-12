from bounded_contexts.adoptions_domain.services import AdoptionAnimalsService
from bounded_contexts.adoptions_domain.views.adoption_animal_views import (
    AdoptionAnimalViewFactory,
)
from common.use_case import BaseUseCase
from infrastructure.database import RepositoryUtils


class BaseAdoptionsUseCase(BaseUseCase):
    def __init__(
        self,
        repository_utils: RepositoryUtils,
        adoption_animal_service: AdoptionAnimalsService,
        adoption_animal_view_factory: AdoptionAnimalViewFactory,
    ) -> None:
        super().__init__(
            repository_utils=repository_utils,
        )

        self.adoption_animal_service = adoption_animal_service
        self.adoption_animal_view_factory = adoption_animal_view_factory
