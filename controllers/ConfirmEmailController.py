from core.classes.SmtpClient import SmtpClient
from core.Controller import (ROUTE_LOADER, Controller, Hooks, HTTPStatus,
                             Request, Response, Utils, datetime, falcon,
                             timezone)
from models.EmailTemplate import EmailTemplate
from models.Session import Session
from models.UserVerification import User, UserVerification


@ROUTE_LOADER('/v1/confirm-email/{action}')
class ConfirmEmailController(Controller):
    def __init__(self):
        self.actions = {
            "request": self.__request,
            "validate-code": self.__validate_code,
        }

    def __request(self, req: Request, resp: Response):
        session = self.get_session(req, resp)
        if not session:
            return

        user: User = session.user

        if user.email_confirmed:
            self.response(resp, HTTPStatus.CONFLICT, error="This user email is already verified")
            return

        user_verification = UserVerification.get_verification_of_user(user)
        if not user_verification:
            self.response(resp, HTTPStatus.INTERNAL_SERVER_ERROR, error="Problem with User Verification")
            return

        user_verification.email_otp = Utils.generate_token()
        user_verification.email_otp_time = datetime.now(timezone.utc)
        if not user_verification.save():
            self.response(resp, HTTPStatus.INTERNAL_SERVER_ERROR, error=self.PROBLEM_SAVING_TO_DB)
            return

        SmtpClient.send_email_to_pool(EmailTemplate.CONFIRM_EMAIL, user.email, {"token": user_verification.email_otp}, send_now=True)

    @falcon.before(Hooks.post_validations, required_attributes={"token": str})
    def __validate_code(self, req: Request, resp: Response, token: str = None):
        data: dict = req.media

        email_code = data["token"]

        user_verification = UserVerification.get(UserVerification.email_otp == str(email_code))
        if not user_verification:
            self.response(resp, HTTPStatus.UNAUTHORIZED, message="Incorrect code")
            return

        if not Utils.validate_expiration_time(user_verification.email_otp_time, "email_code"):
            self.response(resp, HTTPStatus.UNAUTHORIZED, message="code expired")
            return

        user: User = user_verification.user
        user.email_confirmed = 1
        user_verification.email_otp = None
        user_verification.email_otp_time = None
        if not user.save():
            self.response(resp, HTTPStatus.INTERNAL_SERVER_ERROR, error=self.PROBLEM_SAVING_TO_DB)
            return
        user_verification.save()

        self.response(resp, HTTPStatus.OK, message="Email confirmed successfully")

    def on_post(self, req: Request, resp: Response, action: str):
        self.actions[action](req, resp)
