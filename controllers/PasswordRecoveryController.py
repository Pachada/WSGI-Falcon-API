from core.Controller import Controller, Utils, Request, Response, json, datetime
from core.classes.Authenticator import Authenticator
from models.User import User
from models.EmailTemplate import EmailTemplate
from core.classes.SmtpClient import SmtpClient


class PasswordRecoveryController(Controller):
    def __init__(self):
        self.actions = {
            "request": self.__request,
            "validate-code": self.__validate_code,
            "change-password": self.__change_password,
        }

    def __request(self, req: Request, resp: Response):
        try:
            data: dict = json.loads(req.stream.read())
        except Exception as exc:
            print(exc)
            self.response(resp, 400, error=str(exc))
            return

        email = data.get("email")
        if not email:
            self.response(resp, 400, error="email needed")
            return

        user = User.get(User.email == email)
        if not user:
            self.response(resp, 404, error="User not found")
            return

        user.otp = Utils.generate_otp(5)
        user.otp_time = datetime.utcnow()
        if not user.save():
            self.response(resp, 500, self.PROBLEM_SAVING_TO_DB)
            return

        data_for_email = {"otp": user.otp}

        SmtpClient.send_email_to_pool(
            EmailTemplate.PASSWORD_RECOVERY, user, data_for_email, send_now=True
        )

        self.response(resp, 200, message="OTP saved successfully")

    def __validate_code(self, req: Request, resp: Response):
        data: dict = self.get_req_data(req, resp)
        if not data:
            return

        otp = data.get("otp")
        if not otp:
            self.response(resp, 400, message="otp needed")
            return

        user = User.get(User.otp == otp)
        if not user:
            self.response(resp, 401, message="Incorrect code")
            return

        if not Utils.validate_expiration_time(user.otp_time, "otp"):
            self.response(resp, 401, message="code expired")
            return

        device_uuid = data.get("device_uuid", "unknown")
        user.otp = None
        user.otp_time = None
        if not user.save():
            self.response(resp, 500, self.PROBLEM_SAVING_TO_DB)
            return

        session = Authenticator.login_by_otp(user, device_uuid)
        req.context.session = session
        data = {
            "session": Utils.serialize_model(
                req.context.session,
                recursive=True,
                recursiveLimit=3,
                blacklist=["device"],
            ),
        }
        self.response(resp, 200, data, message="Session started")

    def __change_password(self, req: Request, resp: Response):
        data: dict = self.get_req_data(req, resp)
        if not data:
            return

        new_password: str = str(data.get("new_password"))
        if not new_password:
            self.response(resp, 400, error="new_password is required")
            return

        session = req.context.session
        user: User = session.user

        user.password = Utils.get_hashed_string(new_password + user.salt)
        if not user.save():
            self.response(resp, 500, self.PROBLEM_SAVING_TO_DB)
            return

        self.response(resp, 200, message="Password changed successfully")

    def on_post(self, req: Request, resp: Response, action: str):
        self.actions[action](req, resp)
