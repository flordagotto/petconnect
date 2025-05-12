from bounded_contexts.pets_domain.services import PetService
from bounded_contexts.pets_domain.views import PetViewFactory
from common.use_case import BaseUseCase
from infrastructure.database import RepositoryUtils


class BasePetsUseCase(BaseUseCase):
    def __init__(
        self,
        repository_utils: RepositoryUtils,
        pet_service: PetService,
        pet_view_factory: PetViewFactory,
    ) -> None:
        super().__init__(
            repository_utils=repository_utils,
        )

        self.pet_service = pet_service
        self.pet_view_factory = pet_view_factory
