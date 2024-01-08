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
from models.Role import Role 

@ROUTE_LOADER('/test')
class TestController(Controller):
    skip_auth = True

    def on_get(self, req: Request, resp: Response):
        pass

    def on_post(self, req: Request, resp: Response):
        pass
