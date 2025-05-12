from bounded_contexts.social_domain.exceptions import BaseSocialException


class ViewOrganizationalProfilesUnauthorizedException(BaseSocialException):
    def __init__(self, actor_account_id: str) -> None:
        self.actor_account_id = actor_account_id


class RegisterOrganizationAdminUnauthorizedException(BaseSocialException):
    pass


class AcceptOrganizationMemberUnauthorizedException(BaseSocialException):
    def __init__(self, actor_account_id: str) -> None:
        self.actor_account_id = actor_account_id


class DisableOrganizationMemberUnauthorizedException(BaseSocialException):
    def __init__(self, actor_account_id: str) -> None:
        self.actor_account_id = actor_account_id
