import asynctest
from bounded_contexts import initialize_contexts
from common.dependencies import DependencyContainer
from config import ProjectConfig, YamlConfigFileName
from infrastructure.database import RepositoryUtils


class BaseTestConfigSingleton:
    def __init__(self) -> None:
        self.initialized: bool = False
        self.dependencies: DependencyContainer = DependencyContainer()

    async def initialize_contexts_once(self) -> None:
        if self.initialized:
            return

        self.dependencies.register(
            ProjectConfig,
            ProjectConfig(YamlConfigFileName.TESTING),
        )

        initialize_contexts(self.dependencies)

        repository_utils: RepositoryUtils = self.dependencies.resolve(RepositoryUtils)
        await repository_utils.create_metadata()

        self.initialized = True


test_config: BaseTestConfigSingleton = BaseTestConfigSingleton()


class BaseUseCaseTest(asynctest.TestCase):
    async def setUp(self) -> None:
        self.dependencies: DependencyContainer = test_config.dependencies

        await test_config.initialize_contexts_once()

        self.repository_utils: RepositoryUtils = self.dependencies.resolve(
            RepositoryUtils
        )

        await self.repository_utils.dispose_engine()
        await self.repository_utils.clear_database()

    async def tearDown(self) -> None:
        pass

    def get_dependencies(self) -> DependencyContainer:
        return self.dependencies
