from core.Controller import Controller, Utils, Request, Response, json, datetime
from models.Person import Person
from models.User import User
from core.classes.Authenticator import Authenticator


class UserController(Controller):
    def on_get(self, req: Request, resp: Response, id: int = None):
        super().generic_on_get(req, resp, User, id)

    def on_post(self, req: Request, resp: Response, id=None):
        if id:
            self.response(resp, 405)
            return

        try:
            data: dict = json.loads(req.stream.read())
        except Exception as exc:
            print(exc)
            self.response(resp, 400, error=str(exc))

        if data.get("username") and data.get("password"):
            return self.create_user(req, resp, data)

    def on_put(self, req: Request, resp: Response, id: int = None):
        super().generic_on_put(req, resp, User, id)

    def on_delete(self, req: Request, resp: Response, id: int = None):
        super().generic_on_delete(req, resp, User, id)

    # ------------------------------- Utils -------------------------------

    def create_user(self, req: Request, resp: Response, data: dict):
        exists, message = User.check_if_user_exists(
            data.get("username"), data.get("email")
        )
        if exists:
            self.response(resp, 409, error=message)
            return

        user, error_message, code = self.create_user_helper(data)
        if user is None:
            self.response(resp, code, error=error_message)
            return

        session = Authenticator.login(
            user.email, data.get("password"), data.get("device_uuid", "unknown")
        )
        data = {
            "session": Utils.serialize_model(
                session, recursive=True, recursiveLimit=3, blacklist=["device"]
            )
        }
        self.response(resp, 201, data, message="Session started")
        resp.append_header("content_location", f"/users/{user.id}")

    def create_user_helper(self, data: dict):
        if not data.get("password"):
            return None, "Se necesita el campo password", 400

        person = Person(
            firstname=data.get("name"),
            last_name=data.get("last_name"),
            birthday=data.get("birthday"),
        )
        if not person.save():
            return None, self.PROBLEM_SAVING_TO_DB, 500

        password_encrypted = Utils.get_hashed_string(data.get("password"))
        user = User(
            username=data.get("username"),
            password=password_encrypted,
            email=data.get("email"),
            phone=data.get("phone"),
            person_id=person.id,
        )
        if not user.save():
            return None, self.PROBLEM_SAVING_TO_DB, 500

        return user, None, None
