from core.Controller import Controller, Utils, Request, Response, datetime
from models.UserVerification import UserVerification, User
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

        if user.email_confirmed:
            self.response(resp, 409, error="This user email is already verified")
            return

        user_verification = UserVerification.get_verification_of_user(user)
        if not user_verification: 
            self.response(resp, 500, error = "Problema con la Verificación del Usuario")
            return

        user_verification.email_otp = Utils.generate_token()
        user_verification.email_otp_time = datetime.utcnow()
        if not user_verification.save():
            self.response(resp, 500, error=self.PROBLEM_SAVING_TO_DB)
            return

        SmtpClient.send_email_to_pool(
            EmailTemplate.CONFIRM_EMAIL, user, {"token": user_verification.email_otp}, send_now=True
        )

    def __validate_code(self, req: Request, resp: Response, token: str = None):
        data: dict = self.get_req_data(req, resp)
        if not data:
            return

        email_code = data.get("token")
        if not email_code:
            self.response(resp, 400, error="token field is required")
            return

        user_verification = UserVerification.get(UserVerification.otp == str(email_code))
        if not user_verification:
            self.response(resp, 401, message="Incorrect code")
            return

        if not Utils.validate_expiration_time(user_verification.otp_time, "email_code"):
            self.response(resp, 401, message="code expired")
            return

        user: User  = user_verification.user
        user.email_confirmed = 1
        user_verification.email_otp = None
        user_verification.email_otp_time = None
        if not user.save():
            self.response(resp, 500, error=self.PROBLEM_SAVING_TO_DB)
            return
        user_verification.save()

        self.response(resp, 200, message="Email confirmed successfully")

    def on_post(self, req: Request, resp: Response, action: str):
        self.actions[action](req, resp)
