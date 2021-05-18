from datetime import datetime, timedelta
import falcon
import json
import hashlib
import time


class Controller():

    # Error mesages 
    MISSING_OR_EXCESSIVE_PARAMS = "Bad Request - Your request is missing or excessive parameters. Please verify and resubmit."
    PROBLEM_SAVING_TO_DB = "Internal Server Error - problem saving to database."
    INVALID_JSON = "Bad Request - Invalid JSON"
    ID_NOT_FOUND = "Not Found - Invalid ID"
    
    def response(self, resp, http_code=200, data=None, message=None, error=None, error_code=None):
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
            500: falcon.HTTP_500
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

    def set_values(self, row, data:dict):
        try:
            for col in row.__table__.columns.keys():
                if col in data:
                    if col == "password":
                        password = hashlib.sha256(data[col].encode('utf-8')).hexdigest()
                        setattr(row, col, password)
                        continue
                    setattr(row, col, data[col])
            row.save()

        except Exception as exc:
            print("[ERROR-SETTING_VALUES]")
            print(exc)
            return False
