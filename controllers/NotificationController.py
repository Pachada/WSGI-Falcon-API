from core.Controller import Controller, Utils, Request, Response, json, datetime
from models.User import User
from models.PushNotificationSent import PushNotificationSent, and_
from models.PushNotificationPool import PushNotificationPool
from models.Status import Status


class NotificationController(Controller):
    def on_get(self, req: Request, resp: Response, id: int = None):
        user = req.context.session.user
        super().generic_on_get(
            req,
            resp,
            PushNotificationSent,
            id,
            filters=(
                and_(
                    PushNotificationSent.user_id == user.id,
                    PushNotificationSent.status_id == Status.SEND,
                    PushNotificationSent.read == 0,
                )
            ),
        )

    def on_put(self, req: Request, resp: Response, id: int = None):
        try:
            if not id:
                self.response(resp, 405)
                return

            # The id que recevie is the id of a PushNotificationPool object
            # With that id we can get the PushNotificationSent object associated with it
            # and mark it as readed.
            notification = PushNotificationPool.get(id)
            if not notification:
                self.response(resp, 404, error=self.ID_NOT_FOUND)
                return

            notification_sent = PushNotificationSent.get(
                PushNotificationSent.push_notification_pool_id == notification.id
            )
            if not notification_sent:
                self.response(resp, 404, error=self.ID_NOT_FOUND)
                return

            data: dict = json.loads(req.stream.read())
            notification_sent.read = data.get("read", 1)
            notification_sent.save()

            self.response(resp, 200, Utils.serialize_model(notification_sent))
        except Exception as exc:
            print(exc)
            self.response(resp, 400, error=str(exc))
