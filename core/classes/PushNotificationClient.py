import json
from models.User import User
from models.PushNotificationTemplate import PushNotificationTemplate
from models.PushNotificationPool import PushNotificationPool

class PushNotificationClient():
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

    def send_notification_to_pool(self, user:User, template_id:int, data:dict={}, extra:dict={}):
        template = PushNotificationTemplate.get(template_id)
        message_for_notification = f"{template.title}\n{template.message}"
        for key in data:
            message_for_notification = message_for_notification.replace("{{"+key+"}}", data[key])
        
        catalogue = template.catalogue
        if catalogue:
            action = catalogue.action
            if not extra:
                extra = {
                    "action": action
                }
            else:
                extra["action"] = action

        pushNotification = PushNotificationPool(
            user_id=user.id,
            template_id=template.id,
            message = message_for_notification,
            data = json.dumps(extra)
        )
        pushNotification.save()

