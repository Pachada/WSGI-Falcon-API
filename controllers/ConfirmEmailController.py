from core.Controller import Controller, Utils, Request, Response, json, datetime
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
        try:
            session: Session = req.context.session
            user: User = session.user

            email_code = Utils.generate_otp(5)
            user.email_confirmation_code = email_code
            user.email_confirmation_code_time = datetime.utcnow()
            if not user.save():
                self.response(resp, 500, error=self.PROBLEM_SAVING_TO_DB)
                return

            data_for_email = {"email_confirmation_code": email_code}
            client = SmtpClient.get_instance()
            if Utils.check_if_valid_email(user.username):
                client.send_email_to_pool(
                    user.username, data_for_email, EmailTemplate.CONFIRM_EMAIL
                )
            else:
                client.send_email_to_pool(
                    user.email, data_for_email, EmailTemplate.CONFIRM_EMAIL
                )

            self.response(resp, 200, message="Email code saved successfully")

        except Exception as exc:
            print(exc)
            self.response(resp, 400, error=str(exc))

    def __validate_code(self, req: Request, resp: Response):
        try:
            data: dict = json.loads(req.stream.read())
            email_code = data.get("email_code")
            if not email_code:
                self.response(resp, 400, error="email_code needed")
                return

            session: Session = req.context.session
            user: User = session.user

            if email_code != user.email_confirmation_code:
                self.response(resp, 401, error="Incorrect code")
                return

            if not Utils.validate_email_code(user):
                self.response(resp, 401, message="code expired")
                return

            user.confirmed_email = 1
            user.email_confirmation_code = None
            user.email_confirmation_code_time = None
            if not user.save():
                self.response(resp, 500, error=self.PROBLEM_SAVING_TO_DB)
                return

            self.response(resp, 200, message="Email confirmed successfully")
        except Exception as exc:
            print(exc)
            self.response(resp, 400, error=str(exc))

    def on_post(self, req: Request, resp: Response, action: str):
        self.actions[action](req, resp)
