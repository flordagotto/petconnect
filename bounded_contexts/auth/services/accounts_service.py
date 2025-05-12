from uuid import uuid4
from bounded_contexts.auth.entities import Account
from bounded_contexts.auth.enum import TokenTypes
from bounded_contexts.auth.events import (
    PasswordResetRequestEvent,
    ResendVerificationMailRequestEvent,
    AccountVerifiedEvent,
)
from bounded_contexts.auth.exceptions import (
    EmailAlreadyRegisteredException,
    IncorrectLoginDataException,
    AccountNotFoundByEmailException,
    AccountNotFoundByIdException,
    AccountNotVerifiedException,
    UnexpectedTokenException,
    AccountAlreadyVerifiedException,
)
from bounded_contexts.auth.repositories import AccountsRepository
from bounded_contexts.auth.value_objects import TokenData
from config import CryptoConfig
from infrastructure.crypto import HashUtils, TokenUtils
from infrastructure.date_utils import float_timestamp
from infrastructure.uow_abstraction import UnitOfWork


class AccountsService:
    def __init__(
        self,
        crypto_config: CryptoConfig,
        accounts_repository: AccountsRepository,
        hash_utils: HashUtils,
        token_utils: TokenUtils[TokenData],
    ) -> None:
        self.crypto_config = crypto_config
        self.accounts_repository = accounts_repository
        self.hash_utils = hash_utils
        self.token_utils = token_utils

    async def create_account(
        self, uow: UnitOfWork, email: str, password: str
    ) -> Account:
        email = email.strip().lower()
        if await self.accounts_repository.get_account_by_email(
            session=uow.session, email=email
        ):
            raise EmailAlreadyRegisteredException(email=email)

        account: Account = Account(
            entity_id=uuid4().hex,
            email=email,
            password=await self.hash_utils.hash_string(password),
            verified=False,
        )

        await self.accounts_repository.add_account(session=uow.session, account=account)

        return account

    async def get_account_by_email(self, uow: UnitOfWork, email: str) -> Account:
        email = email.strip().lower()
        account: Account | None = await self.accounts_repository.get_account_by_email(
            session=uow.session, email=email
        )

        if not account:
            raise AccountNotFoundByEmailException(email=email)

        return account

    async def get_account_by_id(self, uow: UnitOfWork, account_id: str) -> Account:
        account: Account | None = await self.accounts_repository.get_account_by_id(
            session=uow.session,
            account_id=account_id,
        )

        if not account:
            raise AccountNotFoundByIdException(entity_id=account_id)

        return account

    async def verify_account(self, uow: UnitOfWork, verification_token: str) -> None:
        token_data: TokenData = await self.token_utils.decode_token(
            token=verification_token,
        )

        self.__assert_token_type(
            token_data=token_data, expected_token_type=TokenTypes.VERIFY_ACCOUNT_TOKEN
        )

        account: Account = await self.get_account_by_id(
            uow=uow,
            account_id=token_data.account_id,
        )

        account.verified = True

        self.__issue_account_verified_event(
            uow=uow,
            account=account,
        )

        await self.accounts_repository.flush(session=uow.session)

    async def get_login_token(self, account: Account, password: str) -> str:
        if not await self.hash_utils.verify_hash(password, account.password):
            raise IncorrectLoginDataException(email=account.email)

        if not account.verified:
            raise AccountNotVerifiedException(account_id=account.entity_id)

        return await self.generate_login_token(
            account_id=account.entity_id,
        )

    async def request_password_reset(self, uow: UnitOfWork, email: str) -> None:
        email = email.strip().lower()
        account: Account = await self.get_account_by_email(uow=uow, email=email)

        self.__issue_password_reset_request_event(
            uow=uow,
            account=account,
        )

    async def reset_account_password(
        self,
        uow: UnitOfWork,
        reset_password_token: str,
        new_password: str,
    ) -> None:
        token_data: TokenData = await self.token_utils.decode_token(
            token=reset_password_token,
        )

        self.__assert_token_type(
            token_data=token_data, expected_token_type=TokenTypes.RESET_PASSWORD_TOKEN
        )

        account: Account = await self.get_account_by_id(
            uow=uow,
            account_id=token_data.account_id,
        )

        account.password = await self.hash_utils.hash_string(new_password)

        await self.accounts_repository.flush(session=uow.session)

    async def generate_login_token(self, account_id: str) -> str:
        return await self.token_utils.generate_token(
            TokenData(
                account_id=account_id,
                token_type=TokenTypes.ACCESS_TOKEN,
            )
        )

    async def generate_account_verification_token(self, account_id: str) -> str:
        return await self.token_utils.generate_token(
            TokenData(
                account_id=account_id,
                token_type=TokenTypes.VERIFY_ACCOUNT_TOKEN,
            ),
        )

    async def generate_password_reset_token(self, account_id: str) -> str:
        return await self.token_utils.generate_token(
            TokenData(
                account_id=account_id,
                token_type=TokenTypes.RESET_PASSWORD_TOKEN,
            ),
        )

    async def resend_verification_request(self, uow: UnitOfWork, email: str) -> None:
        email = email.strip().lower()
        account: Account = await self.get_account_by_email(uow=uow, email=email)

        if account.verified:
            raise AccountAlreadyVerifiedException(
                account_id=account.entity_id,
                email=account.email,
            )

        # Raise an event vs sending the mail here?
        # If in the future, emails become obsolete, and we want to send something else instead,
        # we can just change the event handler.
        # Leaving the domain logic unchanged.

        self.__issue_resend_verification_mail_event(uow=uow, account=account)

    @staticmethod
    def __issue_password_reset_request_event(uow: UnitOfWork, account: Account) -> None:
        uow.emit_event(
            PasswordResetRequestEvent(
                actor_account_id=account.entity_id,
                email=account.email,
                issued=float_timestamp(),
            )
        )

    @staticmethod
    def __issue_resend_verification_mail_event(
        uow: UnitOfWork, account: Account
    ) -> None:
        uow.emit_event(
            ResendVerificationMailRequestEvent(
                actor_account_id=account.entity_id,
                email=account.email,
                issued=float_timestamp(),
            )
        )

    @staticmethod
    def __issue_account_verified_event(uow: UnitOfWork, account: Account) -> None:
        uow.emit_event(
            AccountVerifiedEvent(
                actor_account_id=account.entity_id,
                email=account.email,
                issued=float_timestamp(),
            )
        )

    @staticmethod
    def __assert_token_type(
        token_data: TokenData, expected_token_type: TokenTypes
    ) -> None:
        if token_data.token_type != expected_token_type:
            raise UnexpectedTokenException(
                expected_token_type=expected_token_type,
                actual_token_type=token_data.token_type,
            )
