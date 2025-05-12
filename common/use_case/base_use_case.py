from infrastructure.database import RepositoryUtils


class BaseUseCase:
    def __init__(
        self,
        repository_utils: RepositoryUtils,
    ) -> None:
        self.repository_utils: RepositoryUtils = repository_utils
