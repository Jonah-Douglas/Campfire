class BaseService[RepoType]:
    def __init__(self, repository: RepoType) -> None:
        self._repository: RepoType = repository
