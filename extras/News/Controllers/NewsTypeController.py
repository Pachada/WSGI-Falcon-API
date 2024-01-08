from core.Controller import Controller, datetime, HTTPStatus
from core.Utils import Utils
from models.NewsType import NewsType


class NewsTypeController(Controller):
    def on_get(self, req, resp):
        types = NewsType.get_all()
        data = Utils.serialize_model(types)
        self.response(resp, HTTPStatus.OK, data)

    def on_post(self, req, resp):
        pass
