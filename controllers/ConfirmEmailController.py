from core.Controller import Controller, Utils, Request, Response, datetime
from models.User import User
from models.EmailTemplate import EmailTemplate
from core.classes.SmtpClient import SmtpClient
from models.Session import Session


class ConfirmEmailController(Controller):
    def __init__(self):
        self.actions = {
            "request": self.__request,
            "validate-code": self.__validate_code,
        }

    def __request(self, req: Request, resp: Response):
        session: Session = req.context.session
        user: User = session.user
        if user.confirmed_email:
            self.response(resp, 409, error="This user email is already verified")
            return

        email_code = Utils.generate_user_token()
        user.email_confirmation_code = email_code
        user.email_confirmation_code_time = datetime.utcnow()
        if not user.save():
            self.response(resp, 500, error=self.PROBLEM_SAVING_TO_DB)
            return

        data_for_email = {"token": email_code}
        SmtpClient.send_email_to_pool(
            EmailTemplate.CONFIRM_EMAIL, user, data_for_email, send_now=True
        )

    def __validate_code(self, req: Request, resp: Response, token: str = None):
        data: dict = self.get_req_data(req, resp)
        if not data:
            return

        email_code = data.get("token")
        if not email_code:
            self.response(resp, 400, error="token field is required")
            return

        user = User.get(User.email_confirmation_code == email_code)
        if not user:
            self.response(resp, 404, error="Invalid code")
            return

        if not Utils.validate_expiration_time(
            user.email_confirmation_code_time, "email_code"
        ):
            self.response(resp, 401, message="Code expired")
            return

        user.confirmed_email = 1
        user.email_confirmation_code = None
        user.email_confirmation_code_time = None
        if not user.save():
            self.response(resp, 500, error=self.PROBLEM_SAVING_TO_DB)
            return

        self.response(resp, 200, message="Email confirmed successfully")

    def on_post(self, req: Request, resp: Response, action: str):
        self.actions[action](req, resp)
