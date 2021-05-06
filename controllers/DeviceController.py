from core.Controller import Controller, json
from core.Utils import Utils
from models.Device import Device
from models.Session import Session

class DeviceController(Controller):

    def on_put_token(self, req, resp):
        try:
            session:Session = req.context.session
            device:Device = session.device
            if not device:
                self.response(resp, 404, error = 'Device not found')
                return

            data:dict = json.loads(req.stream.read())
            if not data.get('token'):
                self.response(resp, 400, error = 'token needed')
                return
                
            device.token = data.get('token')
            device.save()
            self.response(resp, 200, Utils.serialize_model(device))

        except Exception as exc:
            print(exc)
            self.response(resp, 400, error = str(exc))

    def on_get(self, req, resp, id=None):
        if id:
            device = Device.get(id)
            if not device:
                self.response(resp, 404, error=self.ID_NOT_FOUND)
                return
        else:
            device = Device.getAll()

        self.response(resp, 200, Utils.serialize_model(device))

    def on_post(self, req, resp, id=None):
        if id:
            self.response(resp, 405)
            return

        try:
            data:dict = json.loads(req.stream.read())
            device = Device(uuid = data.get('uuid'), description = data.get('description'), user_id = data.get('user_id'))
            
            if not device.save(): 
                self.response(resp, 500, self.PROBLEM_SAVING_TO_DB)
                return

            self.response(resp, 201, Utils.serialize_model(device))
            resp.append_header('content_location', f"/devices/{device.id}")
        except Exception as exc:
            print(exc)
            self.response(resp, 400, error = str(exc))

    def on_put(self, req, resp, id=None):
        if not id:
            self.response(resp, 405)
            return

        try:
            device = Device.get(id)
            if not device:
                self.response(resp, 404, self.ID_NOT_FOUND)
                return
                
            data:dict = json.loads(req.stream.read())
            self.set_values(device, data)

            self.response(resp, 200, Utils.serialize_model(device))

        except Exception as exc:
            print(exc)
            self.response(resp, 400, error = str(exc))
    
    def on_delete(self, req, resp, id=None):
        if not id:
            self.response(resp, 405)
            return

        device = Device.get(id)
        if not device:
            self.response(resp, 404, self.ID_NOT_FOUND)
            return

        device.soft_delete()
        device.save()
        self.response(resp, 200, Utils.serialize_model(device))