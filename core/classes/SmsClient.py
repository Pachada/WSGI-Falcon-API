from datetime import datetime, timezone

from core.Utils import logger
from crons.SmsCrontab import SmsCrontab
from models.SmsPool import SmsPool, SmsTemplate
from models.User import User


class SmsClient:

    @staticmethod
    def send_sms_to_pool(template_id: int, user, data: dict = None, send_time: datetime = datetime.now(timezone.utc), send_now=False):
        if data is None:
            data = {}

        template = SmsTemplate.get(template_id)
        message = SmsClient.format_message(template, data)

        if isinstance(user, list):
            for item in user:
                SmsClient.save_to_pool(template, message, send_time, item)
            return

        sms_pool = SmsClient.save_to_pool(template, message, send_time, user)
        if not sms_pool:
            logger.error("Could not save sms pool")
            return

        if send_now and send_time.replace(tzinfo=timezone.utc) <= datetime.now(timezone.utc):
            SmsCrontab().send_one_sms(sms_pool)

    @staticmethod
    def format_message(template: SmsTemplate, data: dict):
        message = template.message
        for key, value in data.items():
            message = message.replace("{{" + key + "}}", value)

        return message

    @staticmethod
    def save_to_pool(template: SmsTemplate, message: str, send_time: datetime, user: User):
        sms_pool = SmsPool(
            user_id=user.id,
            template_id=template.id,
            message=message,
            send_time=send_time
        )

        return sms_pool if sms_pool.save() else None
