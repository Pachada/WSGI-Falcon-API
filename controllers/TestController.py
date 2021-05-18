from falcon.response import Response
from falcon.request import Request
from core.Controller import Controller, datetime, json
from core.Utils import Utils
import configparser

class TestController(Controller):

    def on_get(self, req:Request, resp:Response):
        pass
    
    def on_post(self, req:Request, resp:Response):
        pass