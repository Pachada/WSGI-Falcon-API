from core.Controller import Controller, json
from core.Utils import Utils
from models.Status import Status

class StatusController(Controller):

    def on_get(self, req, resp, id=None):
        if id:
            status = Status.get(id)
            if not status:
                self.response(resp, 404, error=self.ID_NOT_FOUND)
                return
        else:
            status = Status.getAll()

        self.response(resp, 200, Utils.serialize_model(status))

    def on_post(self, req, resp, id=None):
        if id:
            self.response(resp,405)
            return

        try:
            data:dict = json.loads(req.stream.read())
            status = Status(description = data.get('description'))
            
            if not status.save(): 
                self.response(resp, 500, self.PROBLEM_SAVING_TO_DB)
                return

            self.response(resp, 201,Utils.serialize_model(status))
            resp.append_header('content_location', f"/status/{status.id}")
        except Exception as exc:
            print(exc)
            self.response(resp, 400, error = str(exc))

    def on_put(self, req, resp, id=None):
        if not id:
            self.response(resp,405)
            return

        try:
            status = Status.get(id)
            if not status:
                self.response(resp, 404, self.ID_NOT_FOUND)
                return
                
            data:dict = json.loads(req.stream.read())
            self.set_values(status, data)

            self.response(resp, 200, Utils.serialize_model(status))

        except Exception as exc:
            print(exc)
            self.response(resp, 400, error = str(exc))
    
    def on_delete(self, req, resp, id=None):
        if not id:
            self.response(resp,405)
            return

        status = Status.get(id)
        if not status:
            self.response(resp, 404, self.ID_NOT_FOUND)
            return

        status.delete()
        self.response(resp, 200, Utils.serialize_model(status))