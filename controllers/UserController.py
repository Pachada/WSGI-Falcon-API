from core.Controller import (
    Controller,
    ROUTE_LOADER,
    Utils, 
    Request, 
    Response, 
    HTTPStatus,
    falcon,
    Decorators,
    Hooks
    )
from models.Person import Person
from models.User import User, Role, List
from core.classes.middleware.Authenticator import Authenticator, Session


@ROUTE_LOADER('/v1/users')
@ROUTE_LOADER('/v1/users/{id:int}')
class UserController(Controller):
    def on_get(self, req: Request, resp: Response, id: int = None):
        super().generic_on_get(req, resp, User, id)

    @Decorators.no_authorization_needed
    @falcon.before(Hooks.post_validations, model = [User, Person])
    def on_post(self, req: Request, resp: Response):
        data = req.media
        self.create_user(req, resp, data)

    @falcon.before(Hooks.put_validations)
    def on_put(self, req: Request, resp: Response, id: int = None):
        session = self.get_session(req, resp)
        if not session:
            return
        user: User = session.user
        user_is_admin = user.role_id == Role.ADMIN
        # If the user.role of the session is admin it can modify every user
        # but if is not an admin it can only modify its own user
        if not user_is_admin and user.id != id:
            self.response(resp, HTTPStatus.UNAUTHORIZED, error="Users can only modify their own users")
            return
        
        # Check if a new role was sended
        data: dict = req.get_media()
        new_role = data.get("role_id")

        # If the user is not an admin and is trying to change their role, deny the request
        if new_role is not None and not user_is_admin:
            self.response(resp, HTTPStatus.UNAUTHORIZED, error="Non-admin users cannot change their roles")
            return

        super().generic_on_put(req, resp, User, id)


    def on_delete(self, req: Request, resp: Response, id: int = None):
        # If the user.role of the session is admin it can delete every user
        # but if is not an admin it can only modify its own user
        session = self.get_session(req, resp)
        if not session:
            return
        user: User = session.user
        if user.role_id != Role.ADMIN and user.id != id:
            self.response(resp, HTTPStatus.UNAUTHORIZED, error="Users can only delete their own users")
            return

        deleted_user: User = super().generic_on_delete(req, resp, User, id, return_row=True)
        if not deleted_user:
            return
        # Delete the person and the sessions of the user
        deleted_user.person.soft_delete()
        sessions: List[Session] = Session.get_all(Session.user_id == deleted_user.id)
        for session in sessions:
            session.soft_delete()

    # ------------------------------- Utils -------------------------------

    def create_user(self, req: Request, resp: Response, data: dict):
        exists, message = User.check_if_user_exists(data.get("username"), data.get("email"))
        if exists:
            self.response(resp, HTTPStatus.CONFLICT, error=message)
            return

        user = self.create_user_helper(req, resp, data)
        if not user:
            return

        session, token = Authenticator.login(
            user.username,
            str(data.get("password")),
            str(data.get("device_uuid", "unknown")),
        )
        
        data = {
            "Bearer": token,
            "session": Utils.serialize_model(session, recursive=True, recursiveLimit=3, blacklist=["device"])
        }
        self.response(resp, HTTPStatus.CREATED, data, message="Session started")
        resp.append_header("content_location", f"/users/{user.id}")

    def create_user_helper(self, req: Request, resp: Response, data: dict):
        person = Person(
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            birthday=data.get("birthday"),
        )
        if not person.save():
            self.response(resp, HTTPStatus.INTERNAL_SERVER_ERROR, error=self.PROBLEM_SAVING_TO_DB)
            return

        salt = Utils.generate_salt()
        password = str(data.get("password")) + salt
        user = User(
            username=data.get("username"),
            password=password,
            salt=salt,
            email=data.get("email"),
            phone=data.get("phone"),
            person_id=person.id,
        )
        if not user.save():
            self.response(resp, HTTPStatus.INTERNAL_SERVER_ERROR, error=self.PROBLEM_SAVING_TO_DB)
            return

        return user
