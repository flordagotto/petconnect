import logging
from uuid import uuid4

from dateutil import parser
import requests
from bounded_contexts.donations_domain.entities import (
    PayerInfo,
    MercadoPagoRequest,
    MercadoPagoResponse,
    MercadoPagoTransaction,
)
import mercadopago

from bounded_contexts.donations_domain.enum import MercadoPagoResponseStatuses
from bounded_contexts.donations_domain.exceptions import (
    MercadoPagoPreferenceNotGeneratedException,
    MercadoPagoTransactionNotApprovedException,
)
from bounded_contexts.donations_domain.repositories import MpTransactionsRepository
from common.background import run_async
from infrastructure.payment_gateway import MerchantData
from infrastructure.uow_abstraction import UnitOfWork


class MercadoPagoService:
    logger: logging.Logger = logging.getLogger(__name__)

    def __init__(
        self,
        access_token: str,
        client_id: str,
        client_secret: str,
        frontend_url: str,
        mp_transactions_repository: MpTransactionsRepository,
    ) -> None:
        self.__ACCESS_TOKEN: str = access_token
        self.__client_id: str = client_id
        self.__client_secret: str = client_secret
        self.__frontend_url: str = frontend_url
        self.mp_transactions_repository: MpTransactionsRepository = (
            mp_transactions_repository
        )

    async def get_access_token_details(self, code: str) -> MerchantData:
        def __sync_request() -> dict:
            response = requests.request(
                method="POST",
                url="https://api.mercadopago.com/oauth/token",
                headers={
                    "Content-Type": "application/json",
                },
                data={
                    "client_id": self.__client_id,
                    "client_secret": self.__client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": f"https://petconnect.icu/profile-foundation/account-verification",
                    "test_token": "true" if "TEST" in self.__ACCESS_TOKEN else "false",
                },
            )

            response_json, status_code = response.json(), response.status_code
            self.logger.info(
                f"MP Merchant data status code: {status_code} response: {response_json}"
            )

            return response_json

        data = await run_async(__sync_request)

        return MerchantData(
            access_token=data["access_token"],
            token_type=data["token_type"],
            expires_in=int(data["expires_in"]),
            scope=data["scope"],
            user_id=int(data["user_id"]),
            refresh_token=data["refresh_token"],
            public_key=data["public_key"],
        )

    async def pay_with_card(
        self, merchant_access_token: str, request: MercadoPagoRequest
    ) -> MercadoPagoResponse:
        sdk = mercadopago.SDK(merchant_access_token)

        payment_data = {
            "transaction_amount": float(request.transaction_amount),
            "token": request.token,
            "description": request.description,
            "installments": request.installments,
            "payment_method_id": request.payment_method_id,
            "payer": {
                "email": request.payer.email,
                "identification": {
                    "type": request.payer.identification_type,
                    "number": request.payer.identification_number,
                },
            },
        }

        if request.application_fee:
            payment_data["application_fee"] = request.application_fee

        payment_response = (sdk.payment().create(payment_data))["response"]

        mercadopago_fee, application_fee = 0, 0
        for fee in payment_response.get("fee_details", []):
            if fee["type"] == "mercadopago_fee":
                mercadopago_fee = fee["amount"]
            elif fee["type"] == "application_fee":
                application_fee = fee["amount"]

        mp_response = MercadoPagoResponse(
            status=payment_response["status"],
            status_detail=payment_response["status_detail"],
            id=payment_response["id"],
            date_approved=payment_response["date_approved"],
            payer=PayerInfo(
                email=request.payer.email,
                identification_type=request.payer.identification_type,
                identification_number=request.payer.identification_number,
                name=request.payer.name,
            ),
            payment_method_id=payment_response["payment_method_id"],
            payment_type_id=payment_response["payment_type_id"],
            refunds=payment_response["refunds"],
            transaction_amount=payment_response["transaction_amount"],
            mercadopago_fee=mercadopago_fee,
            application_fee=application_fee,
        )

        return mp_response

    async def get_mp_preference_id(
        self,
        merchant_access_token: str,
        title: str,
        price: float,
        quantity: int,
        purpose: str,
    ) -> str:
        sdk = mercadopago.SDK(merchant_access_token)

        preference_data = {
            "items": [{"title": title, "unit_price": price, "quantity": quantity}],
            "purpose": purpose,
        }

        preference_response = (sdk.preference().create(preference_data))["response"]

        if preference_response.get("error"):
            raise MercadoPagoPreferenceNotGeneratedException(
                preference_response["error"], preference_response["message"]
            )

        return preference_response["id"]

    async def handle_transaction_response(
        self,
        uow: UnitOfWork,
        mp_response: MercadoPagoResponse,
        donation_campaign_id: str,
    ) -> str:
        mp_transaction_status: MercadoPagoResponseStatuses = (
            MercadoPagoResponseStatuses(mp_response.status.upper())
        )

        mp_transaction = MercadoPagoTransaction(
            entity_id=uuid4().hex,
            status=mp_transaction_status,
            status_detail=mp_response.status_detail,
            payer_email=mp_response.payer.email,
            payer_name=mp_response.payer.name,
            payer_identification_type=mp_response.payer.identification_type,
            payer_identification_number=mp_response.payer.identification_number,
            payment_method_id=mp_response.payment_method_id,
            payment_type_id=mp_response.payment_type_id,
            donation_campaign_id=donation_campaign_id,
        )

        if mp_transaction_status != MercadoPagoResponseStatuses.APPROVED:
            await self.mp_transactions_repository.add_transaction(
                session=uow.session,
                transaction=mp_transaction,
            )
            await uow.commit()

            raise MercadoPagoTransactionNotApprovedException(
                status=mp_response.status, status_detail=mp_response.status_detail
            )

        if mp_response.date_approved:
            mp_transaction.date_approved = parser.isoparse(mp_response.date_approved)

        await self.mp_transactions_repository.add_transaction(
            session=uow.session,
            transaction=mp_transaction,
        )

        return mp_transaction.entity_id
