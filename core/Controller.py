from falcon.response import Response
from falcon.request import Request
from datetime import datetime, timedelta, time
import falcon
import json
from core.Utils import Utils


class Controller:
    """
    The Controller class inherits new controllers classes and
    provide them with methods to return different responses depending its necessity.

    """

    # Error mesages
    MISSING_OR_EXCESSIVE_PARAMS = "Bad Request - Your request is missing or excessive parameters. Please verify and resubmit."
    PROBLEM_SAVING_TO_DB = "Internal Server Error - problem saving to database."
    INVALID_JSON = "Bad Request - Invalid JSON"
    ID_NOT_FOUND = "Not Found - Invalid ID"

    def response(
        self, resp, http_code=200, data=None, message=None, error=None, error_code=None
    ):
        map = {
            200: falcon.HTTP_200,
            201: falcon.HTTP_201,
            400: falcon.HTTP_400,
            401: falcon.HTTP_401,
            403: falcon.HTTP_403,
            404: falcon.HTTP_404,
            405: falcon.HTTP_405,
            409: falcon.HTTP_409,
            413: falcon.HTTP_413,
            500: falcon.HTTP_500,
        }
        resp.status = map[http_code]
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

    def set_values(self, row, data: dict):
        try:
            for col in row.__table__.columns.keys():
                if col in data:
                    if col == "password":
                        password = Utils.get_hashed_string(data[col])
                        setattr(row, col, password)
                        continue

                    setattr(row, col, data[col])

            return row.save()

        except Exception as exc:
            print("[ERROR-SETTING_VALUES]")
            print(exc)
            return False

    def generic_on_get(
        self,
        req: Request,
        resp: Response,
        model,
        id: int = None,
        filters=None,
        order_by=None,
    ):
        if id:
            row = model.get(id)
            if not row:
                self.response(resp, 404, error=self.ID_NOT_FOUND)
                return
        else:
            row = model.getAll(filters, orderBy=order_by)

        self.response(resp, 200, Utils.serialize_model(row))

    def generic_on_post(
        self, req: Request, resp: Response, model, content_location, id: int = None
    ):
        if id:
            self.response(resp, 405)
            return

        try:
            data: dict = json.loads(req.stream.read())
        except Exception as exc:
            print(exc)
            self.response(resp, 400, error=str(exc))
            return

        new_record = model()

        if not self.set_values(new_record, data):
            self.response(resp, 500, self.PROBLEM_SAVING_TO_DB)
            return

        self.response(resp, 201, Utils.serialize_model(new_record))
        resp.append_header("content_location", f"/{content_location}/{new_record.id}")

    def generic_on_put(
        self, req: Request, resp: Response, model, id: int = None, extra_data: dict = {}
    ):
        if not id:
            self.response(resp, 405)
            return

        row = model.get(id)
        if not row:
            self.response(resp, 404, self.ID_NOT_FOUND)
            return
        try:
            data: dict = json.loads(req.stream.read())
        except Exception as exc:
            print(exc)
            self.response(resp, 400, error=str(exc))

        data.update(extra_data)

        if not self.set_values(row, data):
            self.response(resp, 500, self.PROBLEM_SAVING_TO_DB)
            return

        self.response(resp, 200, Utils.serialize_model(row))

    def generic_on_delete(
        self,
        req: Request,
        resp: Response,
        model,
        id: int = None,
        soft_delete=True,
        delete_file=False,
    ):
        if not id:
            self.response(resp, 405)
            return

        row = model.get(id)
        if not row:
            self.response(resp, 404, self.ID_NOT_FOUND)
            return

        data = Utils.serialize_model(row)

        if delete_file:
            row.delete_model_files(req, resp)
            if not row.exists_in_database():  # Checamos que el row aún exista
                self.response(resp, 200, data)
                return

        if soft_delete and not row.soft_delete() or not row.delete():
            self.response(resp, 500, self.PROBLEM_SAVING_TO_DB)
            return

        self.response(resp, 200, data)
