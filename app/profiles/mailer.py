import asyncio
import aiosmtplib
import logging

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.base.settings import Settings

settings = Settings()

log = logging.getLogger('application')


class Mailer:

    loop = asyncio.get_event_loop()
    server = aiosmtplib.SMTP(hostname=settings.EMAIL_HOST,
                             port=int(settings.EMAIL_PORT),
                             loop=loop)

    @staticmethod
    async def send_mail(subject, body, receiver, _charset='utf-8'):
        log.info(f'Sending mail to {receiver}')
        await Mailer.server.connect()
        await Mailer.server.starttls()
        await Mailer.server.login(username=settings.EMAIL_USER_NAME,
                                  password=settings.EMAIL_PASSWORD)
        message = MIMEMultipart('alternative')
        message['From'] = settings.EMAIL_USER_NAME
        message['To'] = receiver
        message['Subject'] = subject

        text = MIMEText(body, 'text', _charset=_charset)
        html = MIMEText(body, 'html', _charset=_charset)
        message.attach(html)
        message.attach(text)
        await Mailer.server.send_message(message)
        log.info(f'Successfuly sent mail to {receiver}, shutting down SMTP')
        Mailer.server.close()
