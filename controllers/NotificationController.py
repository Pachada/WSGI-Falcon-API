from core.Controller import Controller, Utils, Request, Response, json, datetime
from models.User import User
from models.PushNotificationSent import PushNotificationSent, and_
from models.PushNotificationPool import PushNotificationPool


class NotificationController(Controller):
    def on_get(self, req: Request, resp: Response, id: int = None):
        user: User = req.context.session.user
        super().generic_on_get(
            req,
            resp,
            PushNotificationSent,
            id,
            filters=(
                and_(
                    PushNotificationSent.user_id == user.id,
                    PushNotificationSent.read == 0,
                )
            ),
        )

    def on_put(self, req: Request, resp: Response, id: int = None):
        if not id:
            self.response(resp, 405)
            return

        notification_sent = PushNotificationSent.get(id)
        if not notification_sent:
            self.response(resp, 404, error=self.ID_NOT_FOUND)
            return

        data: dict = self.get_req_data(req, resp)
        if not data:
            return
        notification_sent.read = data.get("read", 1)
        if not notification_sent.save():
            self.response(resp, 500, error=self.PROBLEM_SAVING_TO_DB)

        self.response(resp, 200, Utils.serialize_model(notification_sent))
