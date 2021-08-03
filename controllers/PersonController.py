from falcon.response import Response
from falcon.request import Request
from core.Controller import Controller, json
from core.Utils import Utils
from models.Person import Person


class PersonController(Controller):
    def on_get(self, req: Request, resp: Response, id: int = None):
        self.generic_on_get(req, resp, Person, id)

    def on_post(self, req: Request, resp: Response, id: int = None):
        self.generic_on_post(req, resp, Person, "persons", id)

    def on_put(self, req: Request, resp: Response, id: int = None):
        self.generic_on_put(req, resp, Person, id)

    def on_delete(self, req: Request, resp: Response, id: int = None):
        self.generic_on_delete(req, resp, Person, id)
