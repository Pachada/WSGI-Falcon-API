from core.Controller import (
    Controller,
    ROUTE_LOADER,
    Utils, 
    Request, 
    Response, 
    datetime, 
    HTTPStatus
    )

@ROUTE_LOADER('/health-check/{action}') # ping
class HealthCheckController(Controller):
    skip_auth = True
    
    def __init__(self):
        self.actions = {"ping": self.__ping}

    def __ping(self, req: Request, resp: Response):
        self.response(resp, HTTPStatus.OK, {"timestamp": Utils.date_formatter(datetime.utcnow())})

    def on_post(self, req: Request, resp: Response, action: str):
        self.actions[action](req, resp)

    def on_get(self, req: Request, resp: Response, action: str):
        self.actions[action](req, resp)
