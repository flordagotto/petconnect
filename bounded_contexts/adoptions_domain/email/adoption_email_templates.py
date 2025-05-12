from enum import Enum
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template

BASE_DIR = Path(__file__).parent.parent.parent.parent

COMMON_TEMPLATE_PATH = BASE_DIR / "common/templates/"
ADOPTION_TEMPLATE_PATH = BASE_DIR / "bounded_contexts/adoptions_domain/email/templates/"

template_env = Environment(
    loader=FileSystemLoader([str(COMMON_TEMPLATE_PATH), str(ADOPTION_TEMPLATE_PATH)])
)


# Steps to register new email:


# 1- Register .html file name here
class AdoptionEmailTemplates(Enum):
    ADOPTION_APPLICATION_APPROVED_TEMPLATE = "adoption_application_approved.html"
    ADOPTION_APPLICATION_REJECTED_TEMPLATE = "adoption_application_rejected.html"


# 2- Register email subject here
class AdoptionEmailSubjects(Enum):
    ADOPTION_APPLICATION_STATUS_UPDATED = "Respondieron tu solicitud de adopción"


# 3- Create render method below
def render_adoption_application_approved_template(
    profile_name: str,
    owner_name: str,
    animal_name: str,
) -> str:
    template: Template = template_env.get_template(
        AdoptionEmailTemplates.ADOPTION_APPLICATION_APPROVED_TEMPLATE.value
    )

    return template.render(
        profile_name=profile_name, owner_name=owner_name, animal_name=animal_name
    )


def render_adoption_application_rejected_template(
    profile_name: str,
    owner_name: str,
    animal_name: str,
) -> str:
    template: Template = template_env.get_template(
        AdoptionEmailTemplates.ADOPTION_APPLICATION_REJECTED_TEMPLATE.value
    )

    return template.render(
        profile_name=profile_name, owner_name=owner_name, animal_name=animal_name
    )
