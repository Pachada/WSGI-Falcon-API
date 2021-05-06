from core.Controller import Controller, json
from core.Utils import Utils
from models.Role import Role

class RoleController(Controller):

    def on_get(self, req, resp, id=None):
        if id:
            role = Role.get(id)
            if not role:
                self.response(resp, 404, error=self.ID_NOT_FOUND)
                return
        else:
            role = Role.getAll()

        self.response(resp, 200, Utils.serialize_model(role))

    def on_post(self, req, resp, id=None):
        if id:
            self.response(resp,405)
            return

        try:
            data:dict = json.loads(req.stream.read())
            role = Role(name = data.get('name'))
            
            if not role.save(): 
                self.response(resp, 500, self.PROBLEM_SAVING_TO_DB)
                return

            self.response(resp, 201,  Utils.serialize_model(role))
            resp.append_header('content_location', f"/roles/{role.id}")
        except Exception as exc:
            print(exc)
            self.response(resp, 400, error = str(exc))

    def on_put(self, req, resp, id=None):
        if not id:
            self.response(resp,405)
            return

        try:
            role = Role.get(id)
            if not role:
                self.response(resp, 404, self.ID_NOT_FOUND)
                return
                
            data:dict = json.loads(req.stream.read())
            self.set_values(role, data)

            self.response(resp, 200, Utils.serialize_model(role))

        except Exception as exc:
            print(exc)
            self.response(resp, 400, error = str(exc))
    
    def on_delete(self, req, resp, id=None):
        if not id:
            self.response(resp,405)
            return

        role = Role.get(id)
        if not role:
            self.response(resp, 404, self.ID_NOT_FOUND)
            return

        role.soft_delete()
        role.save()
        self.response(resp, 200, Utils.serialize_model(role))