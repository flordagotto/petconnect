import logging
import typing
import jwt
from jwt import DecodeError
from bounded_contexts.auth.exceptions import (
    GenerateTokenException,
    DecodeTokenException,
)
from common.background import run_async

T = typing.TypeVar("T")


class TokenUtils(typing.Generic[T]):
    """Async jwt token utils.
    We use generics to determine the return type of the token payload."""

    logger: logging.Logger = logging.getLogger(__name__)

    def __init__(
        self,
        token_secret: str,
        algorithm: str,
        token_data_to_dict: typing.Callable[[T], dict],
        dict_to_token_data: typing.Callable[[dict], T],
    ) -> None:
        self.token_secret = token_secret
        self.algorithm = algorithm
        self.token_data_to_dict = token_data_to_dict
        self.dict_to_token_data = dict_to_token_data

    async def generate_token(self, payload: T) -> str:
        #  we should expire tokens... if we have time.
        #  If this was a real project, we would have a token blacklist, expiration times, refresh tokens, etc...
        #  but I don't see that it is worth it.

        payload_dict: dict = self.token_data_to_dict(payload)

        def _generate_jwt_sync() -> str:
            # Blocking I/O method, should be run in executor

            try:
                return jwt.encode(
                    payload=payload_dict,
                    key=self.token_secret,
                    algorithm=self.algorithm,
                )

            except Exception as e:
                self.logger.error(f"Error generating token: {e}")
                raise GenerateTokenException(payload=payload_dict)

        return await run_async(_generate_jwt_sync)

    async def decode_token(self, token: str) -> T:
        def _decode_jwt_sync() -> T:
            # Blocking I/O method, should be run in executor
            try:
                payload_dict: dict = jwt.decode(
                    jwt=token, key=self.token_secret, algorithms=[self.algorithm]
                )

                return self.dict_to_token_data(payload_dict)

            except DecodeError as e:
                self.logger.error(f"Error decoding token: {e}")
                raise DecodeTokenException(token=token)

        return await run_async(_decode_jwt_sync)
