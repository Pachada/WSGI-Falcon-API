from falcon.response import Response
from falcon.request import Request
from datetime import datetime, timedelta, time, timezone
from falcon import falcon, code_to_http_status
import json
from core.Utils import Utils, logger
from core.Model import Model, and_, String
from http import HTTPStatus
from core.Hooks import Hooks, Decorators
from engine.Server import route_loader as ROUTE_LOADER
from models.Session import Session


class Controller:
    """
    The Controller class inherits new controllers classes and
    provide them with methods to return different responses depending its necessity.

    """
    # If this resource skips the authenticator middleware, False for deafult
    skip_auth = False
    # A class attribute to store the instance
    _instance = None

    def __new__(cls, *args, **kwargs):
        # Check if the instance already exists
        if cls._instance is None:
            # Create a new instance and store it as a class attribute
            cls._instance = super().__new__(cls, *args, **kwargs)
        # Return the existing instance
        return cls._instance
    
    # Error mesages
    MISSING_OR_EXCESSIVE_PARAMS = "Bad Request - Your request is missing or excessive parameters. Please verify and resubmit."
    PROBLEM_SAVING_TO_DB = "Internal Server Error - problem saving to database."
    INVALID_JSON = "Bad Request - Invalid JSON"
    ID_NOT_FOUND = "Not Found - Invalid ID"
    
    def get_session(self, req: Request, resp: Response) -> Session | None:
        session_id = req.context.token_data.get("session_id")
        session = Session.get(Session.id == session_id)
        if not session:
            self.response(resp, HTTPStatus.UNAUTHORIZED, error="Session not found")
            return
        
        return session

    def response(self, resp: Response, http_code=200, data=None, message=None, error=None, error_code=None):
        resp.status = code_to_http_status(http_code)
        if isinstance(data, list) and not data:
            data = []
        elif not data:
            data = {}
        if message:
            data["message"] = message
        if error:
            data["error"] = error
        if error_code:
            data["error_code"] = error_code
        resp.text = json.dumps(data, ensure_ascii=False)

    def set_values(self, row: Model, data: dict):
        try:
            # filter the data dictionary to only include the columns in the row
            data = {col: data[col] for col in row.__table__.columns.keys() if col in data}
            for key, value in data.items():
                # set the attribute on the row object with the same key
                setattr(row, key, value)

            return row.save()

        except Exception as exc:
            logger.error("[ERROR-SETTING_VALUES]")
            logger.error(exc)
            return False

    def get_req_data(self, req: Request, resp: Response):
        try:
            data: dict = req.get_media()
        except Exception as exc:
            logger.error(exc)
            self.response(resp, HTTPStatus.BAD_REQUEST, error=str(exc))
            return

        return data

    def get_model_object(
        self, req: Request, resp: Response, model: Model, id: int = None
    ):
        if not id:
            self.response(resp, HTTPStatus.METHOD_NOT_ALLOWED)
            return

        row = model.get(id)
        if not row:
            self.response(resp, HTTPStatus.NOT_FOUND, error=self.ID_NOT_FOUND)
            return

        return row

    def generic_on_get(
        self,
        req: Request,
        resp: Response,
        model: Model,
        id: int = None,
        filters=None,
        join=None,
        order_by=None,
        recursive=False,
        recursiveLimit=2
    ):
        """
        This function handles generic GET requests for a given model.
        If an ID is provided, it returns the model object with that ID.
        If query parameters are provided, it returns the model objects that match those parameters.
        If neither ID nor query parameters are provided, it returns all model objects with pagination.
        """
        row = None
        if not isinstance(filters, list):
            query = [filters] if filters is not None else []
        
        if id:
            # if an ID is provided, get the model object with that ID
            if row := self.get_model_object(req, resp, model, id):
                self.response(resp, HTTPStatus.OK, Utils.serialize_model(row, recursive=recursive, recursiveLimit=recursiveLimit))

            return

        if req.params:
            # if query parameters are provided, add the filters to the query
            valid_params = [c.key for c in model.__table__.columns]
            page_parameters = ["page", "per_page"]
            for key, value in req.params.items():
                if key in valid_params:
                    column = getattr(model, key)
                    if isinstance(column.type, String):
                        query.append(column.like(f"%{value}%"))
                    else:
                        query.append(column == value)
                elif key not in page_parameters:
                    # handle the case where an invalid parameter is provided
                    valid_params_str = ', '.join(page_parameters+valid_params)
                    self.response(resp, HTTPStatus.BAD_REQUEST, error=f"Invalid query parameter: {key}. Valid parameters are: {valid_params_str}")
                    return

        # Get the model objects using the filters provides if any and hanldes the pagination
        try:
            per_page = int(req.params.get('per_page', 50))
            page = int(req.params.get('page', 1))
        except ValueError:
            # handle the case where page or per_page are not valid integers
            self.response(resp, HTTPStatus.BAD_REQUEST, error="Invalid value for page or per_page. Both must be integers.")
            return

         # Validate that page and per_page are greater than zero
        if page <= 0 or per_page <= 0:
            self.response(resp, HTTPStatus.BAD_REQUEST, error="Invalid value for page or per_page. Both must be greater than zero.")
            return

        offset = (page - 1) * per_page
        row = model.get_all(filter=and_(*query), join=join, order_by=order_by, limit=per_page, offset=offset)

        # calculate the total number of pages
        total_records = model.count(filter=and_(*query))
        max_page = (total_records + per_page - 1) // per_page
        data = {
            "max_page": max_page,
            "actual_page": page,
            "per_page": per_page,
            "data": Utils.serialize_model(row, recursive=recursive, recursiveLimit=recursiveLimit)
        }

        self.response(resp, HTTPStatus.OK, data)

    def generic_on_post(self, req: Request, resp: Response, model: Model, content_location, id: int = None, data=None, extra_data: dict = None):
        if extra_data is None:
            extra_data = {}
        if id:
            self.response(resp, HTTPStatus.METHOD_NOT_ALLOWED)
            return

        if not data:
            data = self.get_req_data(req, resp)
        if not data:
            return

        data.update(extra_data)

        new_record = model()

        if not self.set_values(new_record, data):
            self.response(resp, HTTPStatus.INTERNAL_SERVER_ERROR, error=self.PROBLEM_SAVING_TO_DB)
            return

        self.response(resp, HTTPStatus.CREATED, Utils.serialize_model(new_record))
        resp.append_header("content_location", f"/{content_location}/{new_record.id}")

    def generic_on_put(self, req: Request, resp: Response, model: Model, id: int = None, extra_data: dict = None, return_row: bool = False):
        if extra_data is None:
            extra_data = {}
        if not id:
            self.response(resp, HTTPStatus.METHOD_NOT_ALLOWED)
            return

        row = self.get_model_object(req, resp, model, id)
        if not row:
            return

        data = self.get_req_data(req, resp)
        if not data:
            return

        data.update(extra_data)

        if not self.set_values(row, data):
            self.response(resp, HTTPStatus.INTERNAL_SERVER_ERROR, self.PROBLEM_SAVING_TO_DB)
            return

        self.response(resp, HTTPStatus.OK, Utils.serialize_model(row))

        if return_row:
            return row

    def generic_on_delete(
        self,
        req: Request,
        resp: Response,
        model: Model,
        id: int = None,
        soft_delete: bool = True,
        delete_file: bool = False,
        return_row: bool = False
    ):
        if not id:
            self.response(resp, HTTPStatus.METHOD_NOT_ALLOWED)
            return

        row = self.get_model_object(req, resp, model, id)
        if not row:
            return

        data = Utils.serialize_model(row)

        if delete_file:
            row.delete_model_files(req, resp)
            if not row.exists_in_database():  # Checamos que el row aún exista
                self.response(resp, HTTPStatus.OK, data)
                return

        deleted = row.soft_delete() if soft_delete else row.delete()
        if not deleted:
            self.response(resp, HTTPStatus.INTERNAL_SERVER_ERROR, error=self.PROBLEM_SAVING_TO_DB)
            return

        self.response(resp, HTTPStatus.OK, data)

        if return_row:
            return row
