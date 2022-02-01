from models.User import User
from models.EmailPool import EmailPool, datetime, EmailTemplate
from crons.SmtpClientCrontab import SmtpClientCrontab


class SmtpClient:

    @staticmethod
    def send_email_to_pool(template_id: int, user, data: dict = None, send_time: datetime = datetime.utcnow(), send_now=False):
        if data is None:
            data = {}
        template = EmailTemplate.get(template_id)
        content = SmtpClient.__format_content(template, data)

        if isinstance(user, list):
            for item in user:
                SmtpClient.__save_to_pool(
                    template, content, send_time, item
                )
            return

        SmtpClient.__save_to_pool(
                    template, content, send_time, user
                )

        if send_now and send_time <= datetime.utcnow():
            client = SmtpClientCrontab.get_instance() 
            client.procces_pool()

    @staticmethod
    def __format_content(template: EmailTemplate, data: dict):
        content = str(template.html)
        for key in data:
            content = content.replace("{{" + key + "}}", data[key])

        return content

    @staticmethod
    def __save_to_pool(
        template: EmailTemplate, 
        content: str,
        send_time: datetime,
        user: User 
        ):
        email_pool = EmailPool(
            user_id=user.id,
            template_id=template.id,
            subject=template.subject,
            content=content,
            send_time=send_time
        )
        
        email_pool.save()

