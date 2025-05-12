from abc import abstractmethod
from typing import Type
from fastapi import (
    HTTPException,
)  # Many modules have this name, be careful when importing

from common.exceptions import BaseDomainException

ErrorContainer = dict[Type[BaseDomainException], HTTPException]


class BaseErrorManager:
    @abstractmethod
    def create_error_dictionary(self) -> ErrorContainer:
        pass
