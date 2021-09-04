from core.Controller import Controller, Utils, Request, Response, json, datetime
from models.Status import Status, and_


class StatusController(Controller):
    def on_get(self, req: Request, resp: Response, id: int = None):
        super().generic_on_get(req, resp, Status, id)

    def on_post(self, req: Request, resp: Response, id: int = None):
        super().generic_on_post(req, resp, Status, "status", id)

    def on_put(self, req: Request, resp: Response, id: int = None):
        super().generic_on_put(req, resp, Status, id)

    def on_delete(self, req: Request, resp: Response, id: int = None):
        super().generic_on_delete(req, resp, Status, id, soft_delete=False)
