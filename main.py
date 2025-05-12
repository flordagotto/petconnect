import logging
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from bounded_contexts import initialize_contexts
from common.dependencies import DependencyContainer
from config import ProjectConfig, YamlConfigFileName
from infrastructure.database import RepositoryUtils
from rest import APIManager

app: FastAPI = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://localhost:8100",
        "http://petconnect.icu",
        "https://petconnect.icu",
        "http://www.petconnect.icu",
        "https://www.petconnect.icu",
        "http://*.petconnect.icu",
        "https://*.petconnect.icu",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def start_app() -> None:
    # Setup logger level (uvicorn overrides this to warning/critical only)
    logging.basicConfig(level=logging.INFO)

    # Create dependency container
    dependencies: DependencyContainer = DependencyContainer()

    # Register project config
    dependencies.register(
        ProjectConfig,
        ProjectConfig(YamlConfigFileName.APP_CONFIG),
    )

    # Initialize bounded contexts
    initialize_contexts(dependencies)

    # Initialize and create metadata & repository utils
    repository_utils: RepositoryUtils = dependencies.resolve(RepositoryUtils)
    await repository_utils.create_metadata()

    # Register FastAPI routes
    api_manager: APIManager = APIManager(
        dependencies=dependencies,
    )

    api_manager.initialize_api(app=app)
