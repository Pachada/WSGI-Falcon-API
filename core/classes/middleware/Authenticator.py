import json
from http import HTTPStatus

from falcon.request import Request
from falcon.response import Response
from sqlalchemy import and_

from core.classes.JWT.JWTUtils import JWTUtils, timedelta, datetime, timezone
from core.Utils import Utils, logger
from models.Device import Device
from models.Session import Session
from models.User import User


class Authenticator(object):

    def process_request(self, req: Request, resp: Response):
        # Process the request before routing it.
        pass

    def process_resource(self, req: Request, resp: Response, resource, params):
        """
        Process the resource and determine whether to skip authentication or perform authentication checks.

        Args:
            req (Request): The incoming request object.
            resp (Response): The outgoing response object.
            resource: The resource being accessed.
            params (dict): The parameters extracted from the request URL.

        Returns:
            None
        """
        if self.should_skip_authentication(req, resource, params):
            req.context.token_data = None
        else:
            self.handle_authentication(req, resp, resource)

    def should_skip_authentication(self, req: Request, resource, params: dict):
        """
        Determine if authentication should be skipped based on the URL and resource method
        The URL is expected to contain an 'api' segment in every URL: v1/api/{resource}

        Args:
            req (Request): The incoming request object.
            resource: The resource being accessed.
            params (dict): The parameters extracted from the request URL.

        Returns:
            bool: True if authentication should be skipped, False otherwise.
        """
        # Check if the 'skip_auth' attribute of the resources is True
        if getattr(resource, 'skip_auth', False):
            return True
        # Check if the method has the attribute 'skip_auth'
        # First we need to get the method 
        # Split the request path into individual parts using '/' as the separator
        url_parts = req.path.split('/')
        # Find the index of the 'api' part in the url_parts list and add 1 to it
        # This will give us the index of the part after 'api'
        api_suffix_index = url_parts.index('api') + 1
        # Slice the url_parts list starting from the part after 'api'
        # If api_suffix_index is greater than the length of url_parts, an empty list is assigned
        url_parts = url_parts[api_suffix_index:] if api_suffix_index < len(url_parts) else []
        # If action or resource_id is present, remove the last part from url_parts: /url/{action|id}
        if params.get('action') or params.get('id'):
            url_parts.pop()
        # Construct the method name by prefixing 'on_' to the lowercase HTTP method of the request
        method_name = 'on_' + req.method.lower()
        # Get the last part of url_parts if it contains more than one element, otherwise assign None
        suffix = url_parts[-1] if len(url_parts) > 1 else None
        # If a suffix is present, append it to the method_name
        if suffix:
            method_name += '_' + suffix
        # Check if the resource has the method_name attribute and if the 'skip_auth' attribute of the method is True
        return hasattr(resource, method_name) and getattr(getattr(resource, method_name), 'skip_auth', False)

    def handle_authentication(self, req, resp, resource):
        """
        Perform authentication checks for the current request.

        Args:
            req (Request): The incoming request object.
            resp (Response): The outgoing response object.
            resource: The resource being accessed.

        Returns:
            None
        """
        if not req.auth or not len(req.auth.strip()):
            logger.info("Bearer missing")
            resource.response(resp, HTTPStatus.UNAUTHORIZED, error="Bearer missing")
            resp.complete = True
            return
        # Verify the token and decode it
        token_data, error = JWTUtils.verify_token(req.auth)
        if error:
            logger.warning(error)
            resource.response(resp, HTTPStatus.UNAUTHORIZED, error=error)
            resp.complete = True
            return

        req.context.token_data = token_data

    def process_response(self, req: Request, resp: Response, resource, req_succeeded):
        # Post-processing of the response (after routing).
        pass

    @staticmethod
    def login(username: str, password: str, device_uuid: str="unknown") -> tuple[Session, str] | tuple[None, None]:
        user = User.get(User.email == username) or User.get(User.username == username)
        if user:
            hashed_password = Utils.get_hashed_string(password + user.salt)
            if hashed_password == user.password:
                session, token = Authenticator.start_user_session(user, device_uuid)
                if session:
                    return session, token

        return None, None

    @staticmethod
    def login_by_otp(user, device_uuid="unknown"):
        return Authenticator.start_user_session(user, device_uuid)

    @staticmethod
    def start_user_session(user: User, device_uuid) -> tuple[Session, str]:
        device = Device.get(and_(Device.user_id == user.id, Device.uuid == device_uuid))

        if device is None:
            device = Device(uuid=device_uuid, user_id=user.id)
            device.save()

        session = Session.get(and_(Session.user_id == user.id, Session.device_id == device.id))

        if session is None:
            session = Session(user_id=user.id, device_id=device.id)
        
        session.updated = datetime.now(timezone.utc)
        session.save()
            
        token_data = {
            "user_id": user.id,
            "device_id": device.id,
            "role_id": user.role_id,
            "session_id": session.id
        }

        return session, JWTUtils.create_token(token_data, timedelta(days=7))

    @staticmethod
    def logout(session: Session):
        return session.soft_delete()
