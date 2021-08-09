import json
from models.User import User, datetime
from models.PushNotificationTemplate import PushNotificationTemplate
from models.PushNotificationPool import PushNotificationPool


class PushNotificationClient:
    __instance = None

    @staticmethod
    def get_instance():
        if not PushNotificationClient.__instance:
            PushNotificationClient()
        return PushNotificationClient.__instance

    def __init__(self):
        if PushNotificationClient.__instance is not None:
            return PushNotificationClient.__instance
        else:
            PushNotificationClient.__instance = self

    def send_notification_to_pool(
        self,
        user: User,
        template_id: int,
        data: dict = {},
        extra: dict = {},
        notification_time: datetime = None,
    ):
        template = PushNotificationTemplate.get(template_id)
        message_for_notification = f"{template.title}\n{template.message}"
        for key in data:
            message_for_notification = message_for_notification.replace(
                "{{" + key + "}}", data[key]
            )

        push_notification = PushNotificationPool(
            user_id=user.id,
            template_id=template.id,
            message=message_for_notification,
            notification_time=notification_time or datetime.utcnow(),
        )

        # we create a new PushNotificationPool object and save it to DB
        # in order to get its id. Then we add that id to the extra object.
        # And save the PushNotificationPool object again.
        push_notification.save()

        extra["notification_id"] = push_notification.id

        catalogue = template.catalogue
        if catalogue:
            extra["action"] = catalogue.action

        push_notification.data = json.dumps(extra)
        push_notification.save()
