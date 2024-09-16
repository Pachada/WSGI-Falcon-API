from core.Controller import (
    Controller,
    Utils,
    Request,
    Response,
    HTTPStatus,
    ROUTE_LOADER,
    falcon,
    Hooks
)
from models.Device import Device, AppVersion
from models.Role import Role


@ROUTE_LOADER('/devices')
@ROUTE_LOADER('/devices/{id:int}')
class DeviceController(Controller):
    def on_put_version(self, req: Request, resp: Response):
        """

        Checks if the version of the app the devices is running is equal or greater then the current app version

        if the version of the device is lower than the current version, returns HTTP_HTTPStatus.CONFLICT code
        else a HTTP_200 code

        """
        data: dict = self.get_req_data(req, resp)
        if not data:
            return

        app_version = AppVersion.get_actual_version_class()
        if float(data.get("device_version", 0.0)) < app_version.version:
            self.response(resp, HTTPStatus.CONFLICT, error="Updated the app in the store")
            return
        
        session = self.get_session(req, resp)
        if not session:
            return
        device: Device = session.device
        if device.app_version_id != app_version.id:
            device.app_version_id = app_version.id
            device.save()

        self.response(resp, HTTPStatus.OK)

    @falcon.before(Hooks.post_validations, required_attributes={"token": str})
    def on_put_token(self, req: Request, resp: Response):
        """
        Adds the notification token to the device of the current session
        """
        
        session = self.get_session(req, resp)
        if not session:
            return
        device: Device = session.device
        data: dict = req.media
        device.token = data.get("token")
        if not device.save():
            self.response(resp, HTTPStatus.INTERNAL_SERVER_ERROR, error=self.PROBLEM_SAVING_TO_DB)
            return

        self.response(resp, HTTPStatus.OK, Utils.serialize_model(device))

    def on_get(self, req: Request, resp: Response, id: int = None):
        super().generic_on_get(req, resp, Device, id)

    def on_put(self, req: Request, resp: Response, id: int = None):
        super().generic_on_put(req, resp, Device, id)

    @falcon.before(Hooks.check_privileges, allowed_roles_ids={Role.ADMIN})
    def on_delete(self, req: Request, resp: Response, id: int = None):
        super().generic_on_delete(req, resp, Device, id)
