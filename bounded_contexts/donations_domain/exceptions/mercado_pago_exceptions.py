from bounded_contexts.donations_domain.exceptions.base_donation_exception import (
    BaseDonationException,
)


class MercadoPagoPreferenceNotGeneratedException(BaseDonationException):
    def __init__(self, error: str, error_detail: str) -> None:
        self.error = error
        self.error_detail = error_detail


class MercadoPagoTransactionNotApprovedException(BaseDonationException):
    def __init__(self, status: str, status_detail: str) -> None:
        self.status = status
        self.status_detail = status_detail
