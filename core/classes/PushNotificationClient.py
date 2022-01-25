import json
from models.User import User, datetime
from models.PushNotificationTemplate import PushNotificationTemplate
from models.PushNotificationPool import PushNotificationPool
#from crons.ExpoPushNotificationCrontab import ExpoPushNotificationCrontab
from crons.PushNotificationCrontabOneSignal import PushNotificationCrontabOneSignal


class PushNotificationClient:
    __instance = None

    @staticmethod
    def get_instance():
        if not PushNotificationClient.__instance:
            return PushNotificationClient()
        return PushNotificationClient.__instance

    def __init__(self):
        if PushNotificationClient.__instance is not None:
            return PushNotificationClient.__instance
        else:
            PushNotificationClient.__instance = self

    def send_notification_to_pool(
        self,
        user, # type: User | list
        template_id: int,
        data: dict = {},
        extra: dict = {},
        send_time: datetime = None,
        send_now=False
    ):
        if isinstance(user, list):
            for item in user:
                self.send_notification_to_pool(item, template_id, data, extra, send_time)
            return

        template = PushNotificationTemplate.get(template_id)
        message = f"{template.title}\n{template.message}"
        for key in data:
            message = message.replace(
                "{{" + key + "}}", data[key]
            )

        push_notification = PushNotificationPool(
            user_id=user.id,
            template_id=template.id,
            message=message,
            notification_time=send_time or datetime.utcnow()
        )

        catalogue = template.catalogue
        if catalogue:
            extra["action"] = catalogue.action

        push_notification.data = json.dumps(extra)
        push_notification.save()

        if not send_now and send_time <= datetime.utcnow():
            #client = ExpoPushNotificationCrontab.get_instance()
            client = PushNotificationCrontabOneSignal.get_instance() 
            client.procces_pool()
