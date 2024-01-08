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
from models.Status import Status
from models.Role import Role

@ROUTE_LOADER('/statuses')
@ROUTE_LOADER('/statuses/{id:int}')
class StatusController(Controller):
    def on_get(self, req: Request, resp: Response, id: int = None):
        super().generic_on_get(req, resp, Status, id)

    @falcon.before(Hooks.check_privileges, allowed_roles_ids={Role.ADMIN})
    @falcon.before(Hooks.post_validations, model = Status)
    def on_post(self, req: Request, resp: Response, id: int = None):
        super().generic_on_post(req, resp, Status, "statuses", id)

    @falcon.before(Hooks.check_privileges, allowed_roles_ids={Role.ADMIN})
    def on_put(self, req: Request, resp: Response, id: int = None):
        super().generic_on_put(req, resp, Status, id)

    @falcon.before(Hooks.check_privileges, allowed_roles_ids={Role.ADMIN})
    def on_delete(self, req: Request, resp: Response, id: int = None):
        super().generic_on_delete(req, resp, Status, id, soft_delete=False)
