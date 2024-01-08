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


@ROUTE_LOADER('/sessions')
@ROUTE_LOADER('/sessions/{action}') # login, logout
class SessionController(Controller):
    def __init__(self):
        self.actions = {
            "login": self.__login,
            "logout": self.__logout,
        }

    def on_get(self, req: Request, resp: Response):
        session: Session = req.context.session
        role: Role = session.user.role

        session_data = Utils.serialize_model(session, recursive=True, recursiveLimit=2)

        session_data["role"] = Utils.serialize_model(role)
        data = {"session": session_data}
        self.response(resp, HTTPStatus.OK, data)

    def __login(self, req: Request, resp: Response):
        data = self.get_req_data(req, resp)
        if not data:
            return

        username = str(data.get("username"))
        password = str(data.get("password"))
        uuid = str(data.get("device_uuid", "unknown"))
        if not username or not password:
            self.response(resp, HTTPStatus.BAD_REQUEST, error="Username and password are required")
            return

        session = Authenticator.login(username, password, uuid)
        if not session:
            self.response(resp, HTTPStatus.UNAUTHORIZED, error="Invalid credentials")
            return

        req.context.session = session
        data = {
            "session": Utils.serialize_model(
                session, recursive=True, recursiveLimit=3, blacklist=["device"]
            )
        }
        self.response(resp, HTTPStatus.OK, data, message="Session started")

    def __logout(self, req: Request, resp: Response):
        session = req.context.session
        Authenticator.logout(session)
        self.response(resp, HTTPStatus.OK, message="Session ended")

    @Decorators.no_authorization_needed
    def on_post(self, req: Request, resp: Response, action: str):
        self.actions[action](req, resp)
