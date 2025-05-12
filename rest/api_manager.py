from fastapi import FastAPI, APIRouter
from common.dependencies import DependencyContainer
from rest.adoptions_domain.adoptions_route_manager import AdoptionsRouteManager
from rest.auth import AuthRouteManager
from rest.donations_domain import DonationsRouteManager
from rest.error_manager.adoptions_error_manager import AdoptionsErrorManager
from rest.error_manager.donations_error_manager import DonationsErrorManager
from rest.error_manager.pets_error_manager import PetsErrorManager
from rest.files.files_route_manager import FilesRouteManager
from rest.pets_domain.pets_route_manager import PetsRouteManager
from rest.reports_domain.reports_route_manager import ReportsRouteManager
from rest.social_domain import SocialRouteManager
from rest.error_manager import AuthErrorManager, ErrorContainer, SocialErrorManager
from rest.error_messages import MessagesConfig


class APIManager:
    def __init__(
        self,
        dependencies: DependencyContainer,
    ) -> None:
        self.dependencies: DependencyContainer = dependencies

    def initialize_api(self, app: FastAPI):
        self._initialize_error_handlers()

        router: APIRouter = APIRouter()

        self.dependencies.register(APIRouter, router)

        # Register routes to router
        self.__register_routes()

        # Register router on app
        app.include_router(router)

    def _initialize_error_handlers(self) -> None:
        messages_config: MessagesConfig = MessagesConfig()
        auth_error_manager: AuthErrorManager = AuthErrorManager(
            messages_config=messages_config
        )
        social_error_manager: SocialErrorManager = SocialErrorManager(
            messages_config=messages_config
        )
        pets_error_manager: PetsErrorManager = PetsErrorManager(
            messages_config=messages_config
        )
        adoptions_error_manager: AdoptionsErrorManager = AdoptionsErrorManager(
            messages_config=messages_config
        )
        donations_error_manager: DonationsErrorManager = DonationsErrorManager(
            messages_config=messages_config
        )

        errors: ErrorContainer = {
            **auth_error_manager.create_error_dictionary(),
            **social_error_manager.create_error_dictionary(),
            **pets_error_manager.create_error_dictionary(),
            **adoptions_error_manager.create_error_dictionary(),
            **donations_error_manager.create_error_dictionary(),
        }

        self.dependencies.register(ErrorContainer, errors)

    def __register_routes(self) -> None:
        self.__register_auth_routes()
        self.__register_social_routes()
        self.__register_pets_routes()
        self.__register_files_routes()
        self.__register_adoptions_routes()
        self.__register_donation_routes()
        self.__register_reports_routes()

    def __register_auth_routes(self) -> None:
        auth_route_manager: AuthRouteManager = AuthRouteManager(
            dependencies=self.dependencies
        )

        auth_route_manager.register_routes()

    def __register_social_routes(self) -> None:
        social_route_manager: SocialRouteManager = SocialRouteManager(
            dependencies=self.dependencies
        )

        social_route_manager.register_routes()

    def __register_pets_routes(self) -> None:
        pets_route_manager: PetsRouteManager = PetsRouteManager(
            dependencies=self.dependencies
        )

        pets_route_manager.register_routes()

    def __register_files_routes(self) -> None:
        files_route_manager: FilesRouteManager = FilesRouteManager(
            dependencies=self.dependencies
        )

        files_route_manager.register_routes()

    def __register_adoptions_routes(self) -> None:
        adoptions_route_manager: AdoptionsRouteManager = AdoptionsRouteManager(
            dependencies=self.dependencies
        )

        adoptions_route_manager.register_routes()

    def __register_donation_routes(self) -> None:
        donations_route_manager: DonationsRouteManager = DonationsRouteManager(
            dependencies=self.dependencies
        )

        donations_route_manager.register_routes()

    def __register_reports_routes(self) -> None:
        reports_route_manager: ReportsRouteManager = ReportsRouteManager(
            dependencies=self.dependencies
        )

        reports_route_manager.register_routes()
