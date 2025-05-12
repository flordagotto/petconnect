from bounded_contexts.social_domain.exceptions import BaseSocialException


class ProfileAlreadyAssociatedToAccountException(BaseSocialException):
    pass


class ProfileNotFoundException(BaseSocialException):
    pass


class PersonalProfileNotFoundException(BaseSocialException):
    pass


class OrganizationalProfileNotFoundException(BaseSocialException):
    pass
