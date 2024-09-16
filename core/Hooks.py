from falcon.response import Response
from falcon.request import Request
from falcon import HTTPBadRequest
from core.Model import Model, datetime, date
from dateutil.parser import parse
from sqlalchemy import inspect
import falcon
from models.User import User, Role


class Hooks:
    """
    To be used with the @falcon.before hook
    """

    @staticmethod
    def check_privileges(req: Request, resp: Response, resource, params, allowed_roles_ids: set[int]):
        " Recibes a list of role_ids that are allowed to access the resource"
        user_role_id: int = req.context.token_data.get("role_id")
        if user_role_id not in allowed_roles_ids:
            raise falcon.HTTPForbidden(description="You don't have permission to access this resource")

    @staticmethod
    def post_validations(req: Request, resp: Response, resource, params, model: Model = None, required_attributes: dict = None):
        try:
            data: dict = req.get_media()
        except Exception as exc:
            raise HTTPBadRequest(description=f"Error getting request body. error: {str(exc)}") from exc

        if model:
            validate_model_required_attributes(data, model)
        if required_attributes:
            validate_required_attributes(data, required_attributes)

    @staticmethod
    def put_validations(req: Request, resp: Response, resource, params):
        # ids are needed for put requests
        if "id" not in params:
            resp.complete = True
            raise HTTPBadRequest(description="Resource id is required")

        try:
            data: dict = req.get_media()
        except Exception as exc:
            raise HTTPBadRequest(description=f"Error getting request body. error: {str(exc)}") from exc


class Decorators:
    # Decorator function to skip authorization
    @staticmethod
    def no_authorization_needed(func):
        func.skip_auth = True
        return func


def validate_model_required_attributes(data, model):
    if model and isinstance(model, (set, list)):
        for item in model:
            validate_model_required_attributes(data, item)
        return

    # Insepct the Model to get it requiered attributes
    inspector = inspect(model)

    required_attributes = {
        column.name: column.type.python_type
        for column in inspector.columns
        if not column.nullable
        and not column.default
        and column.name != "id"
    }

    validate_required_attributes(data, required_attributes)


def validate_required_attributes(data, required_attributes: dict):
    # Iterate over the required attributes
    for attr, attr_type in required_attributes.items():
        # Check if the attribute is present
        if (value := data.get(attr)) is None:
            # If not present, return a response with a 400 code and an error message
            raise HTTPBadRequest(description=f"Missing attribute: {attr}: {attr_type.__name__}")

        # If present, check if the required type is date or datetime to handle accordingly
        if attr_type in (date, datetime):
            # Datetime attributes are sended as strings
            if not isinstance(value, str):
                raise HTTPBadRequest(description=f"Invalid attribute: {attr}. Expected a string with a valid date or datetime format")
            # If so, try to convert it to a date or datetime object using parse()
            try:
                value = parse(value)
            except ValueError as err:
                # If the conversion fails, return a response with a 400 code and an error message
                raise HTTPBadRequest(
                    description=f"Invalid attribute: {attr}. Expected a string with a valid date or datetime format, e.g. YYYY-MM-DDTHH:MM:SS"
                ) from err

        # Check if the converted value has the correct type
        elif not isinstance(value, attr_type):
            # If not, return a response with a 400 code and an error message
            raise HTTPBadRequest(
                description=f"Invalid type for attribute: {attr}. Expected {required_attributes[attr].__name__}, got {type(value).__name__}")
