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

        data: dict = self.get_req_data(req, resp)
        if not data: return

        if data.get("username") and data.get("password"):
            return self.create_user(req, resp, data)

    def on_put(self, req: Request, resp: Response, id: int = None):
        super().generic_on_put(req, resp, User, id)

    def on_delete(self, req: Request, resp: Response, id: int = None):
        super().generic_on_delete(req, resp, User, id)
        #TODO We also delete the person and the sessions of the user

    # ------------------------------- Utils -------------------------------

    def create_user(self, req: Request, resp: Response, data: dict):
        exists, message = User.check_if_user_exists(
            data.get("username"), data.get("email")
        )
        if exists:
            self.response(resp, 409, error=message)
            return

        user = self.create_user_helper(req , resp, data)
        if not user: return

        session = Authenticator.login(
            user.username, str(data.get("password")), str(data.get("device_uuid", "unknown"))
        )
        data = {
            "session": Utils.serialize_model(
                session, recursive=True, recursiveLimit=3, blacklist=["device"]
            )
        }
        self.response(resp, 201, data, message="Session started")
        resp.append_header("content_location", f"/users/{user.id}")

    def create_user_helper(self, req: Request, resp: Response, data: dict):
        if not data.get("password"):
            self.response(resp, 400, "Password field requierd")
            return 

        person = Person(
            first_name=data.get("name"),
            last_name=data.get("last_name"),
            birthday=data.get("birthday"),
        )
        if not person.save():
            self.response(resp, 500, error= self.PROBLEM_SAVING_TO_DB)
            return

        salt = Utils.generate_salt()
        password_encrypted = Utils.get_hashed_string(str(data.get("password")) + salt)
        user = User(
            username=data.get("username"),
            password=password_encrypted,
            salt=salt,
            email=data.get("email"),
            phone=data.get("phone"),
            person_id=person.id,
        )
        if not user.save():
            self.response(resp, 500, error= self.PROBLEM_SAVING_TO_DB)
            return

        return user
