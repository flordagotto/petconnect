from bounded_contexts.auth.services import AccountsService
from bounded_contexts.pets_domain.entities import Pet
from bounded_contexts.pets_domain.services import PetService
from bounded_contexts.pets_domain.use_cases import BasePetsUseCase
from bounded_contexts.pets_domain.views import PetViewFactory, PetAndOwnerView
from bounded_contexts.social_domain.entities import PersonalProfile
from bounded_contexts.social_domain.services.profile_service import ProfileService
from infrastructure.database import RepositoryUtils
from infrastructure.uow_abstraction import UnitOfWork, unit_of_work


class GetPetUseCase(BasePetsUseCase):
    def __init__(
        self,
        repository_utils: RepositoryUtils,
        pet_service: PetService,
        pet_view_factory: PetViewFactory,
        profile_service: ProfileService,
        account_service: AccountsService,
    ) -> None:
        super().__init__(
            repository_utils=repository_utils,
            pet_service=pet_service,
            pet_view_factory=pet_view_factory,
        )

        self.pet_service = pet_service
        self.profile_service = profile_service
        self.account_service = account_service

    @unit_of_work
    async def execute(
        self,
        entity_id: str,
        uow: UnitOfWork,
    ) -> PetAndOwnerView:
        pet: Pet = await self.pet_service.get_pet_by_id(uow=uow, entity_id=entity_id)

        owner: PersonalProfile = await self.profile_service.get_personal_profile(
            uow=uow, entity_id=pet.profile_id
        )
        owner_account = await self.account_service.get_account_by_id(
            uow=uow, account_id=owner.account.entity_id
        )

        return self.pet_view_factory.create_pet_and_owner_view(
            pet=pet,
            owner_name=owner.first_name + " " + owner.surname,
            owner_phone_number=owner.phone_number,
            owner_email=owner_account.email,
            owner_social_media_url=owner.social_media_url,
        )
