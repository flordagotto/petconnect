from enum import Enum
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template

BASE_DIR = Path(__file__).parent.parent.parent.parent

COMMON_TEMPLATE_PATH = BASE_DIR / "common/templates/"
SOCIAL_TEMPLATE_PATH = BASE_DIR / "bounded_contexts/social_domain/email/templates/"

template_env = Environment(
    loader=FileSystemLoader([str(COMMON_TEMPLATE_PATH), str(SOCIAL_TEMPLATE_PATH)])
)


# Steps to register new email:


# 1- Register .html file name here
class SocialEmailTemplates(Enum):
    VERIFY_ACCOUNT_TEMPLATE = "verify_account.html"
    RESET_PASSWORD = "reset_password.html"
    ORGANIZATION_VERIFIED = "organization_verified.html"
    ACCOUNT_VERIFIED_TEMPLATE = "account_verified.html"


# 2- Register email subject here
class SocialEmailSubjects(Enum):
    VERIFY_ACCOUNT = "Verifica tu cuenta"
    RESET_PASSWORD = "Reseteo de contraseña"
    ORGANIZATION_VERIFIED = "Tu organización ha sido verificada"
    ACCOUNT_VERIFIED = "Tu cuenta ha sido verificada"


# 3- Create render method below
def render_verify_account_template(
    profile_name: str,
    verify_account_url: str,
) -> str:
    template: Template = template_env.get_template(
        SocialEmailTemplates.VERIFY_ACCOUNT_TEMPLATE.value
    )

    return template.render(
        profile_name=profile_name,
        verify_account_url=verify_account_url,
    )


def render_reset_password_template(
    profile_name: str,
    reset_password_url: str,
) -> str:
    template: Template = template_env.get_template(
        SocialEmailTemplates.RESET_PASSWORD.value
    )

    return template.render(
        profile_name=profile_name,
        reset_password_url=reset_password_url,
    )


def render_organization_verified_template(
    profile_name: str,
    organization_name: str,
) -> str:
    template: Template = template_env.get_template(
        SocialEmailTemplates.ORGANIZATION_VERIFIED.value
    )

    return template.render(
        profile_name=profile_name,
        organization_name=organization_name,
    )


def render_account_verified_template(profile_name: str) -> str:
    template: Template = template_env.get_template(
        SocialEmailTemplates.ACCOUNT_VERIFIED_TEMPLATE.value
    )

    return template.render(profile_name=profile_name)
