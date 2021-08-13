from models.EmailPool import EmailPool, datetime
from models.EmailTemplate import EmailTemplate


class SmtpClient:
    __instance = None

    @staticmethod
    def get_instance():
        if not SmtpClient.__instance:
            SmtpClient()
        return SmtpClient.__instance

    def __init__(self):
        if SmtpClient.__instance is not None:
            return SmtpClient.__instance
        else:
            SmtpClient.__instance = self

    def send_email_to_pool(
        self,
        receiver_email: str,
        data: dict,
        template_id: int,
        send_time: datetime = None,
    ):
        content, subject = self.__create_message_for_pool(data, template_id)
        self.__save_to_pool(content, receiver_email, template_id, subject, send_time)

    def __create_message_for_pool(self, data: dict, template_id: int):
        template = EmailTemplate.get(template_id)
        content = str(template.html)
        for key in data:
            content = content.replace("{{" + key + "}}", data[key])

        subject = template.subject
        return content, subject

    def __save_to_pool(
        self,
        msg: str,
        email: str,
        template_id: int,
        subject: str,
        send_time: datetime = None,
    ):
        email = EmailPool(
            template_id=template_id,
            content=msg,
            email=email,
            subject=subject,
            send_time=send_time or datetime.utcnow(),
        )

        email.save()
