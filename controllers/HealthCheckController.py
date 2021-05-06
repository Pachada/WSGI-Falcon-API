from core.Controller import Controller, datetime
from core.Utils import Utils

class HealthCheckController(Controller):

    def __init__(self):
        self.actions = {
            'ping': self.__ping
        }

    def __ping(self, req, resp):
        data = {"timestamp":Utils.date_formatter(datetime.utcnow())}
        self.response(resp,200,data)


    def on_post(self, req, resp, action):
        self.actions[action](req, resp)

    def on_get(self, req, resp, action):
        self.actions[action](req, resp)
