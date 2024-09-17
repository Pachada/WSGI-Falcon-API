from core.Controller import (ROUTE_LOADER, Controller, Hooks, HTTPStatus,
                             Request, Response, Utils, falcon)
from models.Role import Role


@ROUTE_LOADER('/v1/test')
class TestController(Controller):
    skip_auth = True

    def on_get(self, req: Request, resp: Response):
        pass

    def on_post(self, req: Request, resp: Response):
        pass
