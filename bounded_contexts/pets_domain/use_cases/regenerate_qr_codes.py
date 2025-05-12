from bounded_contexts.pets_domain.services import PetService
from bounded_contexts.pets_domain.use_cases import BasePetsUseCase
from bounded_contexts.pets_domain.views import PetViewFactory
from bounded_contexts.social_domain.services.profile_service import ProfileService
from infrastructure.database import RepositoryUtils
from infrastructure.uow_abstraction import unit_of_work, UnitOfWork


class RegenerateQrCodesUseCase(BasePetsUseCase):
    def __init__(
        self,
        repository_utils: RepositoryUtils,
        pet_service: PetService,
        pet_view_factory: PetViewFactory,
        profile_service: ProfileService,
    ) -> None:
        super().__init__(
            repository_utils=repository_utils,
            pet_service=pet_service,
            pet_view_factory=pet_view_factory,
        )
        self.profile_service = profile_service

    @unit_of_work
    async def execute(self, uow: UnitOfWork) -> None:
        pets = await self.pet_service.get_all_pets(uow=uow)

        for pet in pets:
            await self.pet_service.regenerate_qr_code(uow, pet=pet)
