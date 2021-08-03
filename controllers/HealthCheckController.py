from falcon.response import Response
from falcon.request import Request
from core.Controller import Controller, datetime
from core.Utils import Utils


class HealthCheckController(Controller):
    def __init__(self):
        self.actions = {"ping": self.__ping}

    def __ping(self, req: Request, resp: Response):
        self.response(resp, 200, {"timestamp": Utils.date_formatter(datetime.utcnow())})

    def on_post(self, req: Request, resp: Response, action: str):
        self.actions[action](req, resp)

    def on_get(self, req: Request, resp: Response, action: str):
        self.actions[action](req, resp)
