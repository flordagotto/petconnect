from bounded_contexts.social_domain.exceptions import BaseSocialException


class OrganizationNotFoundByNameException(BaseSocialException):
    def __init__(self, organization_name: str) -> None:
        self.organization_name = organization_name

    def __str__(self) -> str:
        return f"Exception(name={self.organization_name})"
