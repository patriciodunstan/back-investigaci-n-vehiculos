"""
Servicio de Email.

Implementacion mock para desarrollo, puede ser reemplazada
por una implementacion real con SMTP o servicios como SendGrid.
"""

from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class IEmailService(ABC):
    """Interface para servicio de email."""

    @abstractmethod
    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: bool = False,
    ) -> bool:
        """Envia un email."""
        pass


class MockEmailService(IEmailService):
    """
    Implementacion mock del servicio de email.

    En produccion, reemplazar con implementacion real.
    """

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: bool = False,
    ) -> bool:
        """
        Simula el envio de un email.

        En desarrollo, solo loguea el intento.
        """
        logger.info(
            "EMAIL MOCK - To: %s, Subject: %s, Body: %s...",
            to,
            subject,
            body[:50] if body else "",
        )
        return True


class SMTPEmailService(IEmailService):
    """
    Implementacion real con SMTP.

    Para produccion con configuracion de servidor SMTP.
    """

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        from_email: str,
    ):
        self._smtp_server = smtp_server
        self._smtp_port = smtp_port
        self._username = username
        self._password = password
        self._from_email = from_email

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: bool = False,
    ) -> bool:
        """Envia email via SMTP."""
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self._from_email
            msg["To"] = to

            content_type = "html" if html else "plain"
            msg.attach(MIMEText(body, content_type))

            with smtplib.SMTP(self._smtp_server, self._smtp_port) as server:
                server.starttls()
                server.login(self._username, self._password)
                server.sendmail(self._from_email, to, msg.as_string())

            logger.info("Email enviado exitosamente a %s", to)
            return True
        except Exception as e:
            logger.error("Error enviando email a %s: %s", to, str(e))
            raise
