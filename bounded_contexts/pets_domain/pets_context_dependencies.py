from bounded_contexts.adoptions_domain.services import AdoptionAnimalsService
from bounded_contexts.auth.services import AccountsService
from bounded_contexts.pets_domain.event_handlers import PetEventHandler
from bounded_contexts.pets_domain.repositories import (
    PetsRepository,
    PetsSightRepository,
)
from bounded_contexts.pets_domain.repositories.alchemy import (
    AlchemyPetsRepository,
    AlchemyPetsSightRepository,
)
from bounded_contexts.pets_domain.services.pet_service import PetService
from bounded_contexts.pets_domain.services.pet_sight_service import PetSightService
from bounded_contexts.pets_domain.use_cases import (
    CreatePetUseCase,
    EditPetUseCase,
    RegisterPetSightUseCase,
    GetPetUseCase,
    GetMostRecentLostPetSightsUseCase,
    DeletePetUseCase,
    RegenerateQrCodesUseCase,
)
from bounded_contexts.pets_domain.use_cases.get_pet_sights import GetPetSightsUseCase
from bounded_contexts.pets_domain.use_cases.get_pets import GetPetsUseCase
from bounded_contexts.pets_domain.views import PetViewFactory, PetSightViewFactory
from bounded_contexts.social_domain.repositories import ProfileRepository
from bounded_contexts.social_domain.services.profile_service import ProfileService
from common.dependencies import BaseContextDependencies
from config import ProjectConfig
from infrastructure.database import RepositoryUtils
from infrastructure.email import BaseEmailGateway
from infrastructure.file_system import FileSystemGateway
from infrastructure.qr.qr_code import QRCodeGenerator
from infrastructure.uow_abstraction import EventBus


class PetsContextDependencies(BaseContextDependencies):
    def _initialize_view_factories(self) -> None:
        pet_view_factory: PetViewFactory = PetViewFactory()

        self.dependencies.register(PetViewFactory, pet_view_factory)

        pet_sight_view_factory: PetSightViewFactory = PetSightViewFactory()

        self.dependencies.register(PetSightViewFactory, pet_sight_view_factory)

    def _initialize_repositories(self) -> None:
        pets_repository: PetsRepository = AlchemyPetsRepository()

        self.dependencies.register(PetsRepository, pets_repository)

        pets_sight_repository: PetsSightRepository = AlchemyPetsSightRepository()

        self.dependencies.register(PetsSightRepository, pets_sight_repository)

    def _initialize_services(self) -> None:
        profile_service: ProfileService = ProfileService(
            profile_repository=self.dependencies.resolve(ProfileRepository)
        )

        self.dependencies.register(ProfileService, profile_service)

        pet_service: PetService = PetService(
            pets_repository=self.dependencies.resolve(PetsRepository),
            file_system_gateway=self.dependencies.resolve(FileSystemGateway),
            qr_code=self.dependencies.resolve(QRCodeGenerator),
            url_config=self.dependencies.resolve(ProjectConfig).url_config,
        )

        self.dependencies.register(PetService, pet_service)

        pet_sight_service: PetSightService = PetSightService(
            pets_sight_repository=self.dependencies.resolve(PetsSightRepository)
        )

        self.dependencies.register(PetSightService, pet_sight_service)

    def _initialize_use_cases(self) -> None:
        create_pet: CreatePetUseCase = CreatePetUseCase(
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            pet_service=self.dependencies.resolve(PetService),
            pet_view_factory=self.dependencies.resolve(PetViewFactory),
            profile_service=self.dependencies.resolve(ProfileService),
        )

        self.dependencies.register(CreatePetUseCase, create_pet)

        edit_pet: EditPetUseCase = EditPetUseCase(
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            pet_service=self.dependencies.resolve(PetService),
            pet_view_factory=self.dependencies.resolve(PetViewFactory),
            profile_service=self.dependencies.resolve(ProfileService),
        )

        self.dependencies.register(EditPetUseCase, edit_pet)

        register_pet_sight: RegisterPetSightUseCase = RegisterPetSightUseCase(
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            pet_sight_service=self.dependencies.resolve(PetSightService),
            pet_service=self.dependencies.resolve(PetService),
            pet_sight_view_factory=self.dependencies.resolve(PetSightViewFactory),
        )

        self.dependencies.register(RegisterPetSightUseCase, register_pet_sight)

        get_pet: GetPetUseCase = GetPetUseCase(
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            pet_service=self.dependencies.resolve(PetService),
            pet_view_factory=self.dependencies.resolve(PetViewFactory),
            profile_service=self.dependencies.resolve(ProfileService),
            account_service=self.dependencies.resolve(AccountsService),
        )

        self.dependencies.register(GetPetUseCase, get_pet)

        get_pets: GetPetsUseCase = GetPetsUseCase(
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            pet_service=self.dependencies.resolve(PetService),
            profile_service=self.dependencies.resolve(ProfileService),
            pet_view_factory=self.dependencies.resolve(PetViewFactory),
        )

        self.dependencies.register(GetPetsUseCase, get_pets)

        get_pet_sights: GetPetSightsUseCase = GetPetSightsUseCase(
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            pet_sight_service=self.dependencies.resolve(PetSightService),
            pet_sight_view_factory=self.dependencies.resolve(PetSightViewFactory),
        )

        self.dependencies.register(GetPetSightsUseCase, get_pet_sights)

        get_most_recent_lost_pet_sights: GetMostRecentLostPetSightsUseCase = (
            GetMostRecentLostPetSightsUseCase(
                repository_utils=self.dependencies.resolve(RepositoryUtils),
                pet_sight_service=self.dependencies.resolve(PetSightService),
                pet_sight_view_factory=self.dependencies.resolve(PetSightViewFactory),
            )
        )

        self.dependencies.register(
            GetMostRecentLostPetSightsUseCase, get_most_recent_lost_pet_sights
        )

        delete_pet: DeletePetUseCase = DeletePetUseCase(
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            pet_service=self.dependencies.resolve(PetService),
            profile_service=self.dependencies.resolve(ProfileService),
            pet_sight_service=self.dependencies.resolve(PetSightService),
        )

        self.dependencies.register(DeletePetUseCase, delete_pet)

        regenerate_qr_codes: RegenerateQrCodesUseCase = RegenerateQrCodesUseCase(
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            pet_service=self.dependencies.resolve(PetService),
            profile_service=self.dependencies.resolve(ProfileService),
            pet_view_factory=self.dependencies.resolve(PetViewFactory),
        )

        self.dependencies.register(RegenerateQrCodesUseCase, regenerate_qr_codes)

    def _initialize_event_handlers(self) -> None:
        pet_event_handler: PetEventHandler = PetEventHandler(
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            event_bus=self.dependencies.resolve(EventBus),
            pet_service=self.dependencies.resolve(PetService),
            pet_sight_service=self.dependencies.resolve(PetSightService),
            profile_service=self.dependencies.resolve(ProfileService),
            adoption_animal_service=self.dependencies.resolve(AdoptionAnimalsService),
            email_gateway=self.dependencies.resolve(BaseEmailGateway),
            url_config=self.dependencies.resolve(ProjectConfig).url_config,
        )

        self.dependencies.register(PetEventHandler, pet_event_handler)
