from falcon.response import Response
from falcon.request import Request
import falcon
from falcon.http_status import HTTPStatus


class CORS_Handler(object):
    def process_request(self, req: Request, resp: Response):
        resp.set_header("Access-Control-Allow-Origin", "*")
        resp.set_header("Access-Control-Allow-Methods", "*")
        resp.set_header("Access-Control-Allow-Headers", "*")
        resp.set_header("Access-Control-Max-Age", 1728000)  # 20 days
        if req.method == "OPTIONS":
            resp.complete = True
            raise HTTPStatus(falcon.HTTP_200, body="\n")
