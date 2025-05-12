from bounded_contexts.adoptions_domain.event_handlers.adoption_animal_events_handler import (
    AdoptionAnimalEventHandler,
)
from bounded_contexts.adoptions_domain.event_handlers.adoption_application_events_handler import (
    AdoptionApplicationEventHandler,
)
from bounded_contexts.adoptions_domain.repositories import (
    AdoptionAnimalsRepository,
    AdoptionApplicationsRepository,
)
from bounded_contexts.adoptions_domain.repositories.adoptions_repository import (
    AdoptionsRepository,
)
from bounded_contexts.adoptions_domain.repositories.alchemy import (
    AlchemyAdoptionAnimalsRepository,
    AlchemyAdoptionApplicationsRepository,
)
from bounded_contexts.adoptions_domain.repositories.alchemy.alchemy_adoptions_repository import (
    AlchemyAdoptionsRepository,
)
from bounded_contexts.adoptions_domain.services import (
    AdoptionAnimalsService,
    AdoptionService,
)
from bounded_contexts.adoptions_domain.services.adoption_applications_service import (
    AdoptionApplicationService,
)
from bounded_contexts.adoptions_domain.use_cases import (
    CreateAdoptionAnimalUseCase,
    GetAdoptionAnimalUseCase,
    GetAdoptionAnimalsUseCase,
    EditAdoptionAnimalUseCase,
    DeleteAdoptionAnimalUseCase,
)
from bounded_contexts.adoptions_domain.use_cases.create_adoption_application import (
    CreateAdoptionApplicationUseCase,
)
from bounded_contexts.adoptions_domain.use_cases.edit_adoption_application import (
    EditAdoptionApplicationUseCase,
)
from bounded_contexts.adoptions_domain.use_cases.get_adoption_applications import (
    GetAdoptionApplicationsUseCase,
)
from bounded_contexts.adoptions_domain.views.adoption_animal_views import (
    AdoptionAnimalViewFactory,
)
from bounded_contexts.adoptions_domain.views.adoption_application_views import (
    AdoptionApplicationViewFactory,
)
from bounded_contexts.social_domain.repositories import ProfileRepository
from bounded_contexts.social_domain.services.organization_service import (
    OrganizationService,
)
from bounded_contexts.social_domain.services.profile_service import ProfileService
from bounded_contexts.social_domain.views import ProfileViewFactory
from common.dependencies import BaseContextDependencies
from config import ProjectConfig
from infrastructure.database import RepositoryUtils
from infrastructure.email import BaseEmailGateway
from infrastructure.uow_abstraction import EventBus


class AdoptionsContextDependencies(BaseContextDependencies):
    def _initialize_view_factories(self) -> None:
        adoption_animal_view_factory: AdoptionAnimalViewFactory = (
            AdoptionAnimalViewFactory()
        )

        self.dependencies.register(
            AdoptionAnimalViewFactory, adoption_animal_view_factory
        )

        adoption_application_view_factory: AdoptionApplicationViewFactory = (
            AdoptionApplicationViewFactory()
        )

        self.dependencies.register(
            AdoptionApplicationViewFactory, adoption_application_view_factory
        )

    def _initialize_repositories(self) -> None:
        adoption_animals_repository: AdoptionAnimalsRepository = (
            AlchemyAdoptionAnimalsRepository()
        )

        self.dependencies.register(
            AdoptionAnimalsRepository, adoption_animals_repository
        )

        adoption_applications_repository: AdoptionApplicationsRepository = (
            AlchemyAdoptionApplicationsRepository()
        )

        self.dependencies.register(
            AdoptionApplicationsRepository, adoption_applications_repository
        )

        adoptions_repository: AdoptionsRepository = AlchemyAdoptionsRepository()

        self.dependencies.register(AdoptionsRepository, adoptions_repository)

    def _initialize_services(self) -> None:
        profile_service: ProfileService = ProfileService(
            profile_repository=self.dependencies.resolve(ProfileRepository)
        )

        self.dependencies.register(ProfileService, profile_service)

        adoption_animal_service: AdoptionAnimalsService = AdoptionAnimalsService(
            animals_repository=self.dependencies.resolve(AdoptionAnimalsRepository)
        )

        self.dependencies.register(AdoptionAnimalsService, adoption_animal_service)

        adoption_application_service: AdoptionApplicationService = (
            AdoptionApplicationService(
                applications_repository=self.dependencies.resolve(
                    AdoptionApplicationsRepository
                ),
                adoptions_repository=self.dependencies.resolve(AdoptionsRepository),
                animals_repository=self.dependencies.resolve(AdoptionAnimalsRepository),
            )
        )

        self.dependencies.register(
            AdoptionApplicationService, adoption_application_service
        )

        adoption_service: AdoptionService = AdoptionService(
            adoptions_repository=self.dependencies.resolve(AdoptionsRepository)
        )

        self.dependencies.register(AdoptionService, adoption_service)

    def _initialize_use_cases(self) -> None:
        create_adoption_animal: CreateAdoptionAnimalUseCase = (
            CreateAdoptionAnimalUseCase(
                repository_utils=self.dependencies.resolve(RepositoryUtils),
                adoption_animal_service=self.dependencies.resolve(
                    AdoptionAnimalsService
                ),
                adoption_animal_view_factory=self.dependencies.resolve(
                    AdoptionAnimalViewFactory
                ),
                profile_service=self.dependencies.resolve(ProfileService),
            )
        )

        self.dependencies.register(CreateAdoptionAnimalUseCase, create_adoption_animal)

        get_adoption_animal: GetAdoptionAnimalUseCase = GetAdoptionAnimalUseCase(
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            adoption_animal_service=self.dependencies.resolve(AdoptionAnimalsService),
            adoption_animal_view_factory=self.dependencies.resolve(
                AdoptionAnimalViewFactory
            ),
            profile_service=self.dependencies.resolve(ProfileService),
            organization_service=self.dependencies.resolve(OrganizationService),
        )

        self.dependencies.register(GetAdoptionAnimalUseCase, get_adoption_animal)

        get_adoption_animals: GetAdoptionAnimalsUseCase = GetAdoptionAnimalsUseCase(
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            adoption_animal_service=self.dependencies.resolve(AdoptionAnimalsService),
            adoption_animal_view_factory=self.dependencies.resolve(
                AdoptionAnimalViewFactory
            ),
            profile_service=self.dependencies.resolve(ProfileService),
            organization_service=self.dependencies.resolve(OrganizationService),
        )

        self.dependencies.register(GetAdoptionAnimalsUseCase, get_adoption_animals)

        edit_adoption_animals: EditAdoptionAnimalUseCase = EditAdoptionAnimalUseCase(
            repository_utils=self.dependencies.resolve(RepositoryUtils),
            adoption_animal_service=self.dependencies.resolve(AdoptionAnimalsService),
            adoption_animal_view_factory=self.dependencies.resolve(
                AdoptionAnimalViewFactory
            ),
            profile_service=self.dependencies.resolve(ProfileService),
        )

        self.dependencies.register(EditAdoptionAnimalUseCase, edit_adoption_animals)

        delete_adoption_animals: DeleteAdoptionAnimalUseCase = (
            DeleteAdoptionAnimalUseCase(
                repository_utils=self.dependencies.resolve(RepositoryUtils),
                adoption_animal_service=self.dependencies.resolve(
                    AdoptionAnimalsService
                ),
                profile_service=self.dependencies.resolve(ProfileService),
            )
        )

        self.dependencies.register(DeleteAdoptionAnimalUseCase, delete_adoption_animals)

        create_adoption_application: CreateAdoptionApplicationUseCase = (
            CreateAdoptionApplicationUseCase(
                repository_utils=self.dependencies.resolve(RepositoryUtils),
                adoption_application_service=self.dependencies.resolve(
                    AdoptionApplicationService
                ),
                adoption_application_view_factory=self.dependencies.resolve(
                    AdoptionApplicationViewFactory
                ),
                profile_view_factory=self.dependencies.resolve(ProfileViewFactory),
                profile_service=self.dependencies.resolve(ProfileService),
                animal_service=self.dependencies.resolve(AdoptionAnimalsService),
            )
        )

        self.dependencies.register(
            CreateAdoptionApplicationUseCase, create_adoption_application
        )

        get_adoption_applications: GetAdoptionApplicationsUseCase = (
            GetAdoptionApplicationsUseCase(
                repository_utils=self.dependencies.resolve(RepositoryUtils),
                adoption_application_service=self.dependencies.resolve(
                    AdoptionApplicationService
                ),
                adoption_animals_service=self.dependencies.resolve(
                    AdoptionAnimalsService
                ),
                adoption_application_view_factory=self.dependencies.resolve(
                    AdoptionApplicationViewFactory
                ),
                profile_view_factory=self.dependencies.resolve(ProfileViewFactory),
                animal_view_factory=self.dependencies.resolve(
                    AdoptionAnimalViewFactory
                ),
                profile_service=self.dependencies.resolve(ProfileService),
                organization_service=self.dependencies.resolve(OrganizationService),
            )
        )

        self.dependencies.register(
            GetAdoptionApplicationsUseCase, get_adoption_applications
        )

        edit_adoption_applications: EditAdoptionApplicationUseCase = (
            EditAdoptionApplicationUseCase(
                repository_utils=self.dependencies.resolve(RepositoryUtils),
                adoption_application_service=self.dependencies.resolve(
                    AdoptionApplicationService
                ),
                adoption_application_view_factory=self.dependencies.resolve(
                    AdoptionApplicationViewFactory
                ),
                adoption_animal_service=self.dependencies.resolve(
                    AdoptionAnimalsService
                ),
                profile_service=self.dependencies.resolve(ProfileService),
            )
        )

        self.dependencies.register(
            EditAdoptionApplicationUseCase, edit_adoption_applications
        )

    def _initialize_event_handlers(self) -> None:
        adoption_animal_event_handler: AdoptionAnimalEventHandler = (
            AdoptionAnimalEventHandler(
                repository_utils=self.dependencies.resolve(RepositoryUtils),
                event_bus=self.dependencies.resolve(EventBus),
                adoption_animal_service=self.dependencies.resolve(
                    AdoptionAnimalsService
                ),
                adoption_application_service=self.dependencies.resolve(
                    AdoptionApplicationService
                ),
            )
        )

        self.dependencies.register(
            AdoptionAnimalEventHandler, adoption_animal_event_handler
        )

        adoption_application_event_handler: AdoptionApplicationEventHandler = (
            AdoptionApplicationEventHandler(
                repository_utils=self.dependencies.resolve(RepositoryUtils),
                event_bus=self.dependencies.resolve(EventBus),
                adoption_animal_service=self.dependencies.resolve(
                    AdoptionAnimalsService
                ),
                adoption_application_service=self.dependencies.resolve(
                    AdoptionApplicationService
                ),
                profile_service=self.dependencies.resolve(ProfileService),
                organization_service=self.dependencies.resolve(OrganizationService),
                email_gateway=self.dependencies.resolve(BaseEmailGateway),
                url_config=self.dependencies.resolve(ProjectConfig).url_config,
            )
        )

        self.dependencies.register(
            AdoptionApplicationEventHandler, adoption_application_event_handler
        )
