from falcon.response import Response
from falcon.request import Request
from core.Controller import Controller, json
from core.Utils import Utils
from models.Role import Role


class RoleController(Controller):
    def on_get(self, req: Request, resp: Response, id: int = None):
        self.generic_on_get(req, resp, Role, id)

    def on_post(self, req: Request, resp: Response, id: int = None):
        self.generic_on_post(req, resp, Role, "roles", id)

    def on_put(self, req: Request, resp: Response, id: int = None):
        self.generic_on_put(req, resp, Role, id)

    def on_delete(self, req: Request, resp: Response, id: int = None):
        self.generic_on_delete(req, resp, Role, id)
