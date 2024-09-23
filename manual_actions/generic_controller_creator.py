import os
from manual_actions.create_init_files import create_controllers_init_file

def create_controller(model_name):
    model_file = f"models/{model_name}.py"
    controller_file = f"controllers/{model_name}Controller.py"

    if not os.path.exists(model_file):
        print(f"Model file {model_file} does not exist.")
        return
    
    include_privileges = input("Include check_privileges? (yes/no): ").strip().lower() == 'yes'

    if include_privileges:
        privileges_decorator = """@falcon.before(Hooks.check_privileges, allowed_roles_ids={Role.ADMIN})\n    """
    else:
        privileges_decorator = ""

    controller_content = f"""from core.Controller import (ROUTE_LOADER, Controller, Hooks, HTTPStatus,
                             Request, Response, Utils, falcon)
from models.Role import Role
from models.{model_name} import {model_name}


@ROUTE_LOADER('/v1/{model_name.lower()}s')
@ROUTE_LOADER('/v1/{model_name.lower()}s/{{id:int}}')
class {model_name}Controller(Controller):

    {privileges_decorator}def on_get(self, req: Request, resp: Response, id: int = None):
        super().generic_on_get(req, resp, {model_name}, id)

    {privileges_decorator}def on_post(self, req: Request, resp: Response, id: int = None):
        super().generic_on_post(req, resp, {model_name}, "{model_name.lower()}s", id)

    {privileges_decorator}def on_put(self, req: Request, resp: Response, id: int = None):
        super().generic_on_put(req, resp, {model_name}, id)

    {privileges_decorator}def on_delete(self, req: Request, resp: Response, id: int = None):
        super().generic_on_delete(req, resp, {model_name}, id)
"""

    with open(controller_file, "w") as f:
        f.write(controller_content)

    print(f"Controller {controller_file} created successfully.")

if __name__ == "__main__":
    model_name = input("Enter the model name: ")
    create_controller(model_name)
    create_controllers_init_file()