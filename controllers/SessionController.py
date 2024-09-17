from core.Controller import (
    Controller,
    Utils,
    Request,
    Response,
    HTTPStatus,
    ROUTE_LOADER,
    falcon,
    Hooks,
    Decorators
)
from core.classes.middleware.Authenticator import Authenticator
from models.Session import Session
from models.Role import Role


@ROUTE_LOADER('/v1/sessions')
@ROUTE_LOADER('/v1/sessions/login', suffix="login")
@ROUTE_LOADER('/v1/sessions/logout', suffix="logout")
class SessionController(Controller):

    def on_get(self, req: Request, resp: Response):
        session = self.get_session(req, resp)
        if not session:
            return
        
        data = {
            "session": Utils.serialize_model(session, recursive=True, recursiveLimit=3, blacklist=["device"])
        }
        self.response(resp, HTTPStatus.OK, data)

    @Decorators.no_authorization_needed
    @falcon.before(Hooks.post_validations, required_attributes={"username": str, "password": str})
    def on_post_login(self, req: Request, resp: Response):
        data = self.get_req_data(req, resp)
        if not data:
            return

        username: str = data["username"]
        password: str = data["password"]
        uuid = str(data.get("device_uuid", "unknown"))

        session, token = Authenticator.login(username, password, uuid)
        if not session:
            self.response(resp, HTTPStatus.UNAUTHORIZED, error="Invalid credentials")
            return

        data = {
            "Bearer": token,
            "session": Utils.serialize_model(session, recursive=True, recursiveLimit=3, blacklist=["device"])
        }
        
        self.response(resp, HTTPStatus.OK, data, message="Session started")

    def on_post_logout(self, req: Request, resp: Response):
        session = self.get_session(req, resp)
        if not session:
            return
        
        Authenticator.logout(session)
        self.response(resp, HTTPStatus.OK, message="Session ended")