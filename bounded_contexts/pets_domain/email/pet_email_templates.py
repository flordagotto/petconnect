from enum import Enum
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template

BASE_DIR = Path(__file__).parent.parent.parent.parent

COMMON_TEMPLATE_PATH = BASE_DIR / "common/templates/"
PET_TEMPLATE_PATH = BASE_DIR / "bounded_contexts/pets_domain/email/templates/"

template_env = Environment(
    loader=FileSystemLoader([str(COMMON_TEMPLATE_PATH), str(PET_TEMPLATE_PATH)])
)


# Steps to register new email:


# 1- Register .html file name here
class PetEmailTemplates(Enum):
    PET_SIGHT_TEMPLATE = "pet_sight.html"


# 2- Register email subject here
class PetEmailSubjects(Enum):
    PET_SIGHT = "Hubo un avistamiento de tu mascota"


# 3- Create render method below
def render_pet_sight_template(
    profile_name: str,
    lost_pets_url: str,
) -> str:
    template: Template = template_env.get_template(
        PetEmailTemplates.PET_SIGHT_TEMPLATE.value
    )

    return template.render(
        profile_name=profile_name,
        lost_pets_url=lost_pets_url,
    )
