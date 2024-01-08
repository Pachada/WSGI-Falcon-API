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


@ROUTE_LOADER('/roles')
@ROUTE_LOADER('/roles/{id:int}')
class RoleController(Controller):
    
    @falcon.before(Hooks.check_privileges, allowed_roles_ids={Role.ADMIN})
    def on_get(self, req: Request, resp: Response, id: int = None):
        super().generic_on_get(req, resp, Role, id)

    @falcon.before(Hooks.check_privileges, allowed_roles_ids={Role.ADMIN})
    def on_post(self, req: Request, resp: Response, id: int = None):
        super().generic_on_post(req, resp, Role, "roles", id)

    @falcon.before(Hooks.check_privileges, allowed_roles_ids={Role.ADMIN})
    def on_put(self, req: Request, resp: Response, id: int = None):
        super().generic_on_put(req, resp, Role, id)

    @falcon.before(Hooks.check_privileges, allowed_roles_ids={Role.ADMIN})
    def on_delete(self, req: Request, resp: Response, id: int = None):
        super().generic_on_delete(req, resp, Role, id)
