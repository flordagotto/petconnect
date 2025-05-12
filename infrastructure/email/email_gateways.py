import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from python_http_client import HTTPError
from sendgrid import (
    Email as SendGridEmail,
    SendGridAPIClient,
    To as SendGridTo,
    Mail as SendGridMail,
    From as SendGridFrom,
)
from common import run_fire_forget


@dataclass
class EmailData:
    sender: str
    recipient: str
    subject: str
    body: str


class BaseEmailGateway(ABC):
    logger: logging.Logger = logging.getLogger(__name__)

    """
    Base email gateway, which provides a template on how should all other (probably twilio, testing or smtp ones)
    should behave. Sending mails must be non-blocking, we must handle the http/smtp details in the background.
    """

    def __init__(self) -> None:
        self._email_cache: list[EmailData] = []

    def clear_cache(self) -> None:
        self._email_cache.clear()

    @property
    def email_cache(self) -> list[EmailData]:
        return self._email_cache

    def schedule_mail(
        self,
        recipient: str,
        subject: str,
        body: str,
    ) -> None:
        """Non-blocking sync operation of adding the email to the async loop,
        Email will be sent when it is able to.
        No need to await this function."""

        email_data: EmailData = EmailData(
            sender=self._get_sender_details(),
            recipient=recipient,
            subject=subject,
            body=body,
        )

        self.email_cache.append(email_data)

        # This sends the task in the background, it will get executed 'eventually'.
        run_fire_forget(lambda: self._send_mail(email_data=email_data))

    @abstractmethod
    def _send_mail(self, email_data: EmailData) -> None:
        """Actually perform the I/O blocking operation of sending a mail. BLOCKING OPERATION, run only in
        run_fire_forget_mode, or in an async manner on the background."""
        pass

    @abstractmethod
    def _get_sender_details(self) -> str:
        pass


class TestEmailGateway(BaseEmailGateway):
    def _send_mail(self, email_data: EmailData) -> None:
        self.logger.info(
            f"Sending email to '{email_data.recipient}' with subject '{email_data.subject}': \n"
            f"{email_data.body}"
        )

    def _get_sender_details(self) -> str:
        return "testing@pet-connect.com"


class SendgridEmailGateway(BaseEmailGateway):
    def __init__(self, api_key: str, from_email_address: str) -> None:
        super().__init__()
        self.sendgrid_client: SendGridAPIClient = SendGridAPIClient(api_key=api_key)
        self.from_email: SendGridEmail = SendGridEmail(from_email_address)

    def _send_mail(self, email_data: EmailData) -> None:
        # docs: https://docs.sendgrid.com/for-developers/sending-email/quickstart-python

        from_email = SendGridFrom(name="Pet Connect", email=self.from_email.email)
        to_email = SendGridTo(email_data.recipient)

        mail = SendGridMail(
            from_email, to_email, email_data.subject, html_content=email_data.body
        )

        mail_json = mail.get()

        try:
            self.sendgrid_client.client.mail.send.post(request_body=mail_json)

        except HTTPError as error:
            self.logger.error(error)

    def _get_sender_details(self) -> str:
        return self.from_email.email
