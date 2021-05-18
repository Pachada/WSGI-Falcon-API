from falcon.response import Response
from falcon.request import Request
from core.Controller import Controller, json
from core.Utils import Utils
from models.User import User
from models.PushNotificationSent import PushNotificationSent, and_
from models.PushNotificationPool import PushNotificationPool
from models.Status import Status

class NotificationController(Controller):

    def on_get(self, req:Request, resp:Response, id:int=None):
        try:
            session = req.context.session
            user: User = session.user
            if not user:
                self.response(resp, 404, error = 'user not found')
                return

            if id:
                notifications_not_seen  = PushNotificationSent.get(id)
                if not notifications_not_seen:
                    self.response(resp, 404, error = self.ID_NOT_FOUND)
                    return

            else:        
                notifications_not_seen = PushNotificationSent.getAll(
                    and_(
                        PushNotificationSent.user_id == user.id,
                        PushNotificationSent.status_id == Status.SEND,
                        PushNotificationSent.read == 0
                ))

            self.response(resp, 200, Utils.serialize_model(notifications_not_seen))
            
        except Exception as exc:
            print(exc)
            self.response(resp, 400, error = str(exc))

    def on_put(self, req:Request, resp:Response, id:int=None):
        try:
            if not id:
                self.response(resp, 405)
                return

            # The id que recevie is the id of a PushNotificationPool object
            # With that id we can get the PushNotificationSent object associated with it
            # and mark it as readed.
            notification = PushNotificationPool.get(id)
            if not notification:
                self.response(resp, 404, error = self.ID_NOT_FOUND)
                return

            notification_sent = PushNotificationSent.get(PushNotificationSent.push_notification_pool_id == notification.id)
            if not notification_sent:
                self.response(resp, 404, error = self.ID_NOT_FOUND)
                return

            data:dict = json.loads(req.stream.read())
            notification_sent.read = data.get('read', 1)
            notification_sent.save()

            self.response(resp, 200, Utils.serialize_model(notification_sent))
        except Exception as exc:
            print(exc)
            self.response(resp, 400, error = str(exc))