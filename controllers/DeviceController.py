from falcon.response import Response
from falcon.request import Request
from core.Controller import Controller, json
from core.Utils import Utils
from models.Device import Device
from models.Session import Session


class DeviceController(Controller):
    def on_put_token(self, req: Request, resp: Response):
        session: Session = req.context.session
        device: Device = session.device
        if not device:
            self.response(resp, 404, error="Device not found")
            return

        try:
            data: dict = json.loads(req.stream.read())
        except Exception as exc:
            print(exc)
            self.response(resp, 400, error=str(exc))
            return

        if not data.get("token"):
            self.response(resp, 400, error="token needed")
            return

        device.token = data.get("token")
        if not device.save():
            self.response(resp, 500, error=self.PROBLEM_SAVING_TO_DB)
            return

        self.response(resp, 200, Utils.serialize_model(device))

    def on_get(self, req: Request, resp: Response, id: int = None):
        self.generic_on_get(req, resp, Device, id)

    def on_put(self, req: Request, resp: Response, id: int = None):
        self.generic_on_put(req, resp, Device, id)

    def on_delete(self, req: Request, resp: Response, id: int = None):
        self.generic_on_delete(req, resp, Device, id)
