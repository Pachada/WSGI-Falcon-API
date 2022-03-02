from falcon.response import Response
from falcon.request import Request
from models.Session import Session
from core.Utils import Utils
import json
from datetime import datetime

class Authenticator(object):

    def __init__(self):
        self.exceptions = []
        self.privileges_tree = self.__load_privileges_tree()
    
    def __load_privileges_tree(self):
        with open("core/roles/roles.json", "r") as roles_file:
            roles_data:dict = json.load(roles_file)
            privilegesTree = []
            for role in roles_data:
                role_privileges = {"role": role["role"], "privileges":  self.__get_privileges(role["role"], roles_data)}
                privilegesTree.append(role_privileges)
            return privilegesTree

    def __get_privileges(self, role_name:str, roles_data:dict):
        groups = []
        privileges = []
        for role in roles_data:
            if role['role'] == role_name:
                groups.extend(iter(role['groups']))
                privileges.extend(iter(role['privileges']))
                break

        if not privileges and not groups:
            return

        privileges_from_groups = []
        if groups:
            with open("core/roles/groups.json", "r") as groups_file:
                groups_data = json.load(groups_file)
                for group in groups_data:
                    if group['group'] in groups:
                        privileges_from_groups.extend(iter(group['privileges']))
        permits = []
        if privileges or privileges_from_groups:
            with open("core/roles/privileges.json", "r") as privileges_file:
                privileges_data = json.load(privileges_file)
                for privilege in privileges_data:
                    if privilege["name"] in privileges or privilege["name"] in privileges_from_groups:
                        privilege_dict = {"method": privilege["method"], "resource": privilege["resource"]}
                        permits.append(privilege_dict)

        if not permits:
            return
        return permits

    def __has_privileges(self, role_name, method, resource):
        privileges = next(
            (
                role["privileges"]
                for role in self.privileges_tree
                if role["role"] == role_name
            ),
            [],
        )

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

    def add_exception_route(self, route):
        self.exceptions.append(route)

    def process_request(self, req:Request, resp:Response):
        #Process the request before routing it.
        pass

    def process_resource(self, req:Request, resp:Response, resource, params):
        if req.path in self.exceptions:
            req.context.session = None
        else:
            session = Session.get(Session.token == req.auth)
            if not session:
                print("No session")
                resource.response(resp, 401, error = "Unauthorized")
                resp.complete = True
                return

            if not Utils.validate_session(session):
                self.logout(session)
                print("Session expired")
                resource.response(resp, 401, message = "Session expired")
                resp.complete = True
                return

            role_name = session.user.role.name
            method = req.method
            resource_name = type(resource).__name__
            if not self.__has_privileges(role_name, method, resource_name):
                print("Not privileges")
                resource.response(resp, 401, message = "Unauthorized")
                resp.complete = True
                return
                
            # update the session.updated to now
            session.updated = datetime.utcnow()
            session.save()
            req.context.session = session

    def process_response(self, req:Request, resp:Response, resource, req_succeeded):
        #Post-processing of the response (after routing).
        pass
