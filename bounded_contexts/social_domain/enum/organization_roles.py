from enum import Enum


class OrganizationRoles(Enum):
    ADMIN: str = "organization_admin"
    MANAGER: str = "organization_manager"
    COLLABORATOR: str = "organization_collaborator"
