from bounded_contexts.adoptions_domain.animal_context_dependencies import (
    AdoptionsContextDependencies,
)
from bounded_contexts.auth.auth_context_dependencies import AuthContextDependencies
from bounded_contexts.donations_domain.donations_context_dependencies import (
    DonationsContextDependencies,
)
from bounded_contexts.pets_domain.pets_context_dependencies import (
    PetsContextDependencies,
)
from bounded_contexts.reports_domain.reports_context_dependencies import (
    ReportsContextDependencies,
)
from bounded_contexts.social_domain.social_context_dependencies import (
    SocialContextDependencies,
)
from bounded_contexts.auth.value_objects import TokenData
from common.dependencies import DependencyContainer
from config import ProjectConfig, S3Config
from infrastructure.crypto import HashUtils, TokenUtils
from infrastructure.database import RepositoryUtils
from infrastructure.email import (
    BaseEmailGateway,
    TestEmailGateway,
    SendgridEmailGateway,
)
from infrastructure.file_system import (
    FileSystemGateway,
    Boto3S3FileSystemGateway,
    TestingFileSystemGateway,
)
from infrastructure.qr.qr_code import QRCodeGenerator, PyQRGenerator
from infrastructure.uow_abstraction import EventBus, app_event_bus


def initialize_contexts(dependencies: DependencyContainer) -> None:
    __initialize_infrastructure(dependencies=dependencies)
    __initialize_repository_utils(dependencies=dependencies)

    auth_context_dependencies: AuthContextDependencies = AuthContextDependencies(
        dependencies=dependencies
    )
    auth_context_dependencies.initialize()

    social_context_dependencies: SocialContextDependencies = SocialContextDependencies(
        dependencies=dependencies
    )
    social_context_dependencies.initialize()

    adoptions_context_dependencies: AdoptionsContextDependencies = (
        AdoptionsContextDependencies(dependencies=dependencies)
    )

    adoptions_context_dependencies.initialize()

    pets_context_dependencies: PetsContextDependencies = PetsContextDependencies(
        dependencies=dependencies
    )
    pets_context_dependencies.initialize()

    donations_context_dependencies: DonationsContextDependencies = (
        DonationsContextDependencies(dependencies=dependencies)
    )
    donations_context_dependencies.initialize()

    reports_context_dependencies: ReportsContextDependencies = (
        ReportsContextDependencies(dependencies=dependencies)
    )
    reports_context_dependencies.initialize()


def __initialize_infrastructure(
    dependencies: DependencyContainer,
) -> None:
    dependencies.register(
        EventBus,
        app_event_bus,
    )

    dependencies.register(HashUtils, HashUtils())

    project_config: ProjectConfig = dependencies.resolve(ProjectConfig)

    token_utils: TokenUtils[TokenData] = TokenUtils(
        algorithm=project_config.crypto.algorithm,
        token_secret=project_config.crypto.token_secret,
        token_data_to_dict=TokenData.to_dict,
        dict_to_token_data=TokenData.from_dict,
    )

    dependencies.register(
        TokenUtils[TokenData],
        token_utils,
    )

    s3_config: S3Config = dependencies.resolve(ProjectConfig).s3_config

    if s3_config.fake:
        testing_file_system_gateway = TestingFileSystemGateway()
        dependencies.register(
            FileSystemGateway,
            testing_file_system_gateway,
        )

    else:
        s3_file_system_gateway = Boto3S3FileSystemGateway(
            bucket_name=s3_config.bucket_name,
            aws_access_key_id=s3_config.aws_access_key_id,
            aws_secret_access_key=s3_config.aws_secret_access_key,
        )

        # Not part of the domain, only of infrastructure in some specific API routes.
        dependencies.register(
            Boto3S3FileSystemGateway,
            s3_file_system_gateway,
        )

        dependencies.register(
            FileSystemGateway,
            s3_file_system_gateway,
        )

    qr_code_generator = PyQRGenerator()

    dependencies.register(
        QRCodeGenerator,
        qr_code_generator,
    )

    if project_config.email.email_environment == "sendgrid":
        dependencies.register(
            BaseEmailGateway,
            SendgridEmailGateway(
                api_key=project_config.email.sendgrid_api_key,
                from_email_address=project_config.email.sendgrid_from_email,
            ),
        )
    else:
        dependencies.register(
            BaseEmailGateway,
            TestEmailGateway(),
        )


def __initialize_repository_utils(
    dependencies: DependencyContainer,
) -> None:
    project_config: ProjectConfig = dependencies.resolve(ProjectConfig)

    repository_utils: RepositoryUtils = RepositoryUtils(
        db_config=project_config.database
    )

    dependencies.register(RepositoryUtils, repository_utils)
