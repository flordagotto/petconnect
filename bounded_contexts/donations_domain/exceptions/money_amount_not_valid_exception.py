from bounded_contexts.donations_domain.exceptions.base_donation_exception import (
    BaseDonationException,
)


class MoneyAmountNotValidException(BaseDonationException):
    def __init__(self) -> None:
        pass
