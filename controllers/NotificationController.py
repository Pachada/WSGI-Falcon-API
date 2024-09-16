from core.Controller import (
    Controller,
    Utils,
    Request,
    Response,
    HTTPStatus,
    ROUTE_LOADER,
    falcon,
    Hooks
)
from models.User import User
from models.PushNotificationSent import PushNotificationSent, and_


@ROUTE_LOADER('/notifications')
@ROUTE_LOADER('/notifications/{id:int}')
class NotificationController(Controller):
    def on_get(self, req: Request, resp: Response, id: int = None):
        user_id: int = req.context.token_data.get("user_id")
        super().generic_on_get(
            req,
            resp,
            PushNotificationSent,
            id,
            filters=(
                and_(
                    PushNotificationSent.user_id == user_id,
                    PushNotificationSent.readed == 0,
                )
            ),
        )

    @falcon.before(Hooks.put_validations)
    def on_put(self, req: Request, resp: Response, id: int = None):
        notification_sent = PushNotificationSent.get(id)
        if not notification_sent:
            self.response(resp, HTTPStatus.NOT_FOUND, error=self.ID_NOT_FOUND)
            return

        data: dict = req.media
        
        notification_sent.read = data.get("read", 1)
        if not notification_sent.save():
            self.response(resp, HTTPStatus.INTERNAL_SERVER_ERROR, error=self.PROBLEM_SAVING_TO_DB)

        self.response(resp, HTTPStatus.OK, Utils.serialize_model(notification_sent))
