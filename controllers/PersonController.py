from core.Controller import Controller, json
from core.Utils import Utils
from models.Person import Person

class PersonController(Controller):

    def on_get(self, req, resp, id=None):
        if id:
            person = Person.get(id)
            if not person:
                self.response(resp, 404, error = self.ID_NOT_FOUND)
                return
        else:
            person = Person.getAll()

        self.response(resp, 200, Utils.serialize_model(person))

    def on_post(self, req, resp, id=None):
        if id:
            self.response(resp,405)
            return

        try:
            data:dict = json.loads(req.stream.read())
            person = Person(first_name=data.get('first_name'), last_name=data.get('last_name'), 
                            birthday=data.get('birthday'), nickname=data.get('nickname'), 
                            gender=data.get('gender'))
            
            if not person.save(): 
                self.response(resp, 500, self.PROBLEM_SAVING_TO_DB)
                return

            self.response(resp, 201, Utils.serialize_model(person))
            resp.append_header('content_location', f"/persons/{person.id}")
        except Exception as exc:
            print(exc)
            self.response(resp, 400, error = str(exc))

    def on_put(self, req, resp, id=None):
        if not id:
            self.response(resp,405)
            return

        try:
            person = Person.get(id)
            if not person:
                self.response(resp, 404, self.ID_NOT_FOUND)
                return
                
            data:dict = json.loads(req.stream.read())
            self.set_values(person, data)

            person_serialized = Utils.serialize_model(person)
            self.response(resp, 200, person_serialized)

        except Exception as exc:
            print(exc)
            self.response(resp, 400, error = str(exc))
    
    def on_delete(self, req, resp, id=None):
        if not id:
            self.response(resp,405)
            return

        person = Person.get(id)
        if not person:
            self.response(resp, 404, self.ID_NOT_FOUND)
            return

        person.soft_delete()
        person.save()
        self.response(resp, 200, Utils.serialize_model(person))