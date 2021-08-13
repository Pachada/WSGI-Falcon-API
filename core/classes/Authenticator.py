from falcon.response import Response
from falcon.request import Request
from models.Session import Session
from models.User import User
from models.Device import Device
from core.Utils import Utils
import base64
import os
from sqlalchemy import and_
import json


class Authenticator(object):
    def __init__(self):
        self.exceptions = []
        self.privileges_tree = self.__load_privileges_tree()

    def __load_privileges_tree(self):
        with open("core/roles/roles.json", "r") as roles_file:
            roles_data: dict = json.load(roles_file)
            privilegesTree = []
            for role in roles_data:
                role_privileges = {
                    "role": role["role"],
                    "privileges": self.__get_privileges(role["role"], roles_data),
                }
                privilegesTree.append(role_privileges)
            return privilegesTree

    def __get_privileges(self, role_name: str, roles_data: dict):
        groups = []
        privileges = []
        for role in roles_data:
            if role["role"] == role_name:
                for group in role["groups"]:
                    groups.append(group)
                for privilege in role["privileges"]:
                    privileges.append(privilege)
                break

        if not privileges and not groups:
            return

        privileges_from_groups = []
        if groups:
            with open("core/roles/groups.json", "r") as groups_file:
                groups_data = json.load(groups_file)
                for group in groups_data:
                    if group["group"] in groups:
                        for privilege in group["privileges"]:
                            privileges_from_groups.append(privilege)

        permits = []
        if privileges or privileges_from_groups:
            with open("core/roles/privileges.json", "r") as privileges_file:
                privileges_data = json.load(privileges_file)
                for privilege in privileges_data:
                    if (
                        privilege["name"] in privileges
                        or privilege["name"] in privileges_from_groups
                    ):
                        privilege_dict = {
                            "method": privilege["method"],
                            "resource": privilege["resource"],
                        }
                        permits.append(privilege_dict)

        if not permits:
            return
        return permits

    def __has_privileges(self, role_name, method, resource):
        privileges = []
        for role in self.privileges_tree:
            if role["role"] == role_name:
                privileges = role["privileges"]
                break
        if not privileges:
            return False

        resources = [
            privilege["resource"]
            for privilege in privileges
            if privilege["method"] == method
        ]

        if not resources:
            return False

        return resource in resources

    def __role_privileges(self, role_name):
        for role in self.privileges_tree:
            if role["role"] == role_name:
                return role["privileges"]

    def add_exception_route(self, route):
        self.exceptions.append(route)

    def process_request(self, req: Request, resp: Response):
        # Process the request before routing it.
        pass

    def process_resource(self, req: Request, resp: Response, resource, params):
        if req.path in self.exceptions:
            req.context.session = None
        else:
            session = Session.get(Session.token == req.auth)
            if not session:
                print("No session")
                resource.response(resp, 401, error="Unauthorized")
                resp.complete = True
                return

            if not Utils.validate_session(session):
                print("Session expired")
                self.logout(session)
                resource.response(resp, 401, message="Session expired")
                resp.complete = True
                return

            role_name = session.user.role.name
            method = req.method
            resource_name = type(resource).__name__
            if not self.__has_privileges(role_name, method, resource_name):
                print("No privileges")
                resource.response(resp, 401, message="Unauthorized")
                resp.complete = True
                return

            req.context.session = session

    def process_response(self, req: Request, resp: Response, resource, req_succeeded):
        # Post-processing of the response (after routing).
        pass

    @staticmethod
    def login(username, password, device_uuid="unknown"):
        user = User.get(User.username == username)
        if user:
            password = Utils.get_hashed_string(password)
            if password == user.password:
                session = Authenticator.start_user_session(user, device_uuid)
                if session:
                    return session
        return None

    @staticmethod
    def login_by_otp(user, device_uuid="unknown"):
        return Authenticator.start_user_session(user, device_uuid)

    @staticmethod
    def start_user_session(user: User, device_uuid):
        device = Device.get(and_(Device.user_id == user.id, Device.uuid == device_uuid))

        if device is None:
            device = Device(
                uuid=device_uuid,
                user_id=user.id,
            )
            device.save()

        session = Session.get(
            and_(Session.user_id == user.id, Session.device_id == device.id)
        )

        if session is None:
            session = Session(user_id=user.id, device_id=device.id)

        session.token = Authenticator.generate_user_token()
        session.save()
        return session

    @staticmethod
    def generate_user_token(nbytes=32):
        tok = os.urandom(nbytes)
        return base64.urlsafe_b64encode(tok).rstrip(b"=").decode("ascii")

    @staticmethod
    def logout(session: Session):
        return session.soft_delete()
