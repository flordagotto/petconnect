from pathlib import Path

AUTH_TEMPLATE_PATH: str = "bounded_contexts/auth/email/templates/"


def get_project_path() -> str:
    return str(Path(__file__).parent.parent.parent.parent)
