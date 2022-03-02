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