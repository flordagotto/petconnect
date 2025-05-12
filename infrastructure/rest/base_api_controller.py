import logging
from abc import abstractmethod
from functools import wraps
from typing import Callable, Any, ParamSpec, TypeVar, Awaitable, Annotated
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

from bounded_contexts.auth.value_objects import TokenData
from common.dependencies import DependencyContainer
from common.exceptions import BaseDomainException
from infrastructure.crypto import TokenUtils
from rest.error_manager import ErrorContainer

P = ParamSpec("P")
R = TypeVar("R")


def handle_domain_exceptions(
    func: Callable[P, Awaitable[R]], errors: ErrorContainer
) -> Callable[P, Awaitable[R]]:
    logger: logging.Logger = logging.getLogger(__name__)

    BASE_500_EXCEPTION: HTTPException = HTTPException(
        status_code=500,
        detail="Hubo un error, intente nuevamente.",
    )

    @wraps(func)
    async def wrapped(*args: Any, **kwargs: Any) -> R:
        try:
            # Try to execute the route...
            result = await func(*args, **kwargs)
            return result

        # Some domain exception happens:
        except BaseDomainException as domain_exception:
            http_error: HTTPException | None = errors.get(
                domain_exception.__class__, None
            )

            # If there is an associated http_error to it, raise it
            if http_error:
                raise http_error

            # If not, raise a 500 exception (this should never happen...)

            logger.error(
                f"An unexpected domain exception happened: {domain_exception.__class__.__name__} - {domain_exception}"
            )
            raise BASE_500_EXCEPTION

        # Any unexpected (postgres, etc...) exception will raise a 500 error. We have to log it, so we can fix it
        # This can and will happen eventually
        except BaseException as e:
            logger.error(
                f"An unexpected domain exception happened: {e.__class__.__name__} - {e}"
            )
            raise BASE_500_EXCEPTION

    return wrapped


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

TokenDependency = Annotated[str, Depends(oauth2_scheme)]
OptionalTokenDependency = Annotated[str, Depends(optional_oauth2_scheme)]


class BaseAPIController:
    POST_ENDPOINT: list[str] = ["POST"]
    PUT_ENDPOINT: list[str] = ["PUT"]
    DELETE_ENDPOINT: list[str] = ["DELETE"]

    def __init__(self, dependencies: DependencyContainer) -> None:
        self.dependencies: DependencyContainer = dependencies
        self.__api_router: APIRouter = dependencies.resolve(APIRouter)
        self.errors: ErrorContainer = dependencies.resolve(ErrorContainer)
        self.token_utils: TokenUtils[TokenData] = dependencies.resolve(
            TokenUtils[TokenData]
        )

    @abstractmethod
    def register_routes(self) -> None:
        pass

    def _register_post_route(
        self, path: str, method: Callable[P, Awaitable[R]]
    ) -> None:
        self.__api_router.add_api_route(
            path,
            methods=self.POST_ENDPOINT,
            endpoint=handle_domain_exceptions(method, errors=self.errors),
        )

    def _register_put_route(self, path: str, method: Callable[P, Awaitable[R]]) -> None:
        self.__api_router.add_api_route(
            path,
            methods=self.PUT_ENDPOINT,
            endpoint=handle_domain_exceptions(method, errors=self.errors),
        )

    def _register_delete_route(
        self, path: str, method: Callable[P, Awaitable[R]]
    ) -> None:
        self.__api_router.add_api_route(
            path,
            methods=self.DELETE_ENDPOINT,
            endpoint=handle_domain_exceptions(method, errors=self.errors),
        )

    def _register_redirect_route(
        self,
        path: str,
        method: Callable[P, Awaitable[R]],
        response_class,
    ) -> None:
        self.__api_router.add_api_route(
            path,
            endpoint=handle_domain_exceptions(
                method,
                errors=self.errors,
            ),
            response_class=response_class,
            status_code=301,
        )

    def _register_get_route(
        self,
        path: str,
        method: Callable[P, Awaitable[R]],
        response_model=None,
    ) -> None:
        # By default, not specifying the methods will register a GET route

        self.__api_router.add_api_route(
            path,
            endpoint=handle_domain_exceptions(
                method,
                errors=self.errors,
            ),
            response_model=response_model
            if response_model
            else method.__annotations__["return"],  # type: ignore
        )

    async def _get_token_data(self, token: str) -> TokenData:
        return await self.token_utils.decode_token(token)
