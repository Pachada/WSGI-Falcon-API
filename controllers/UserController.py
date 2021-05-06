import hashlib
from core.Controller import Controller, json
from core.Utils import Utils
from models.User import User
from core.classes.Authenticator import Authenticator

class UserController(Controller):

    def on_get(self, req, resp, id=None):
        if id:
            user = User.get(id)
            if not user:
                self.response(resp, 404, error=self.ID_NOT_FOUND)
                return
        else:
            user = User.getAll()

        self.response(resp, 200, Utils.serialize_model(user))

    def on_post(self, req, resp, id=None):
        # TODO: How to avoid someone getting the endpoint and the body it receives
        # and creates a root user?
        if id:
            self.response(resp,405)
            return

        try:
            data:dict = json.loads(req.stream.read())
            exists, message = User.check_if_user_exists(data.get('username'), data.get('email'))
            if exists:
                self.response(resp, 409, error = message)
                return

            password:str = data.get('password')
            password_encrypted = hashlib.sha256(password.encode('utf-8')).hexdigest()
            user = User(username = data.get('username'), password = password_encrypted, email = data.get('email'),
                        phone = data.get('phone'), role_id = data.get('role_id'), person_id = data.get('person_id'))
            
            if not user.save(): 
                self.response(resp, 500, self.PROBLEM_SAVING_TO_DB)
                return
            
            session = Authenticator.login(user.username, password, data.get("device_uuid", "unknown"))

            self.response(resp, 201, Utils.serialize_model(session, recursive=True, recursiveLimit=2))
            resp.append_header('content_location', f"/users/{user.id}")
        except Exception as exc:
            print(exc)
            self.response(resp, 400, error = str(exc))

    def on_put(self, req, resp, id=None):
        if not id:
            self.response(resp,405)
            return

        try:
            user = User.get(id)
            if not user:
                self.response(resp, 404, self.ID_NOT_FOUND)
                return
                
            data:dict = json.loads(req.stream.read())
            self.set_values(user, data)

            self.response(resp, 200, Utils.serialize_model(user))

        except Exception as exc:
            print(exc)
            self.response(resp, 400, error = str(exc))
    
    def on_delete(self, req, resp, id=None):
        if not id:
            self.response(resp,405)
            return

        user = User.get(id)
        if not user:
            self.response(resp, 404, self.ID_NOT_FOUND)
            return

        user.soft_delete()
        user.save()
        self.response(resp, 200, Utils.serialize_model(user))