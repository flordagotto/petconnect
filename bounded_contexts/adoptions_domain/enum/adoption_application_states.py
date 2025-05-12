from enum import Enum


class AdoptionApplicationStates(Enum):
    PENDING: str = "PENDING"
    ACCEPTED: str = "ACCEPTED"
    REJECTED: str = "REJECTED"
