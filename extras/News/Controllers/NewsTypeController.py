from core.Controller import Controller, datetime
from core.Utils import Utils
from models.NewsType import NewsType


class NewsTypeController(Controller):
    def on_get(self, req, resp):
        types = NewsType.getAll()
        data = Utils.serialize_model(types)
        self.response(resp, 200, data)

    def on_post(self, req, resp):
        pass
