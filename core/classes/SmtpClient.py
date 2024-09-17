from datetime import datetime, timezone

from jinja2 import Template

from core.Utils import logger
from crons.SmtpClientCrontab import SmtpClientCrontab
from models.EmailPool import EmailPool, EmailTemplate, datetime
from models.User import User


class SmtpClient:

    @staticmethod
    def send_email_to_pool(template_id: int, email, data: dict = None, send_time: datetime = datetime.now(timezone.utc), send_now=False, jinja2=False):
        if data is None:
            data = {}
        template = EmailTemplate.get(template_id)
        if jinja2:
            content = SmtpClient.format_content_jinja2(template, data)
        else:
            content = SmtpClient.format_content(template, data)

        if isinstance(email, list):
            for item in email:
                SmtpClient.save_to_pool(template, item, content, send_time, send_now, jinja2)
            return

        email_pool = SmtpClient.save_to_pool(template, content, send_time, email)
        if not email_pool:
            logger.error("Couldn't save email pool")
            return

        if send_now and send_time.replace(tzinfo=timezone.utc) <= datetime.now(timezone.utc):
            client = SmtpClientCrontab()
            client.send_one_email(email_pool)

    @staticmethod
    def format_content(template: EmailTemplate, data: dict):
        content = str(template.html)
        for key, value in data.items():
            content = content.replace("{{" + key + "}}", value)

        return content

    @staticmethod
    def format_content_jinja2(template: EmailTemplate, data: dict):
        jinja_template = Template(str(template.html))

        return jinja_template.render(data=data)

    @staticmethod
    def save_to_pool(template: EmailTemplate, content: str, send_time: datetime, email: str):
        email_pool = EmailPool(
            email=email,
            template_id=template.id,
            subject=template.subject,
            content=content,
            send_time=send_time
        )

        return email_pool if email_pool.save() else None
