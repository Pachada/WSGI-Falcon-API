from core.Controller import (
    Controller,
    Utils,
    Request,
    Response,
    HTTPStatus,
    ROUTE_LOADER,
    falcon,
    Hooks,
    Decorators, 
    datetime,
    timezone
)
from core.classes.middleware.Authenticator import Authenticator
from models.UserVerification import UserVerification, User
from models.EmailTemplate import EmailTemplate
from core.classes.SmtpClient import SmtpClient
from core.classes.SmsClient import SmsClient, SmsTemplate


@ROUTE_LOADER('/v1/password-recovery/{action}') # request, validate-code
@ROUTE_LOADER('/v1/password-recovery/change-password', suffix="change_password")
class PasswordRecoveryController(Controller):
    def __init__(self):
        self.actions = {
            "request": self.__request,
            "validate-code": self.__validate_code
        }

    def __request(self, req: Request, resp: Response):
        data: dict = self.get_req_data(req, resp)
        if not data:
            return
    
        email = data.get('email')
        phone_number = data.get('phone_number')
        if not email and not phone_number:
            self.response(resp, HTTPStatus.BAD_REQUEST, error="Email or phone number is required")
            return
    
        if phone_number:
            value = (User.phone == str(phone_number))
        else:
            value = (User.email == str(email))
    
        user = User.get(value)
        if not user:
            self.response(resp, HTTPStatus.NOT_FOUND, error="User not found")
            return
    
        user_verification = UserVerification.get_verification_of_user(user)
        if not user_verification:
            self.response(resp, HTTPStatus.INTERNAL_SERVER_ERROR, error="Problem with User Verification")
            return
    
        user_verification.otp = Utils.generate_otp(5)
        user_verification.otp_time = datetime.now(timezone.utc)
        if not user_verification.save():
            self.response(resp, HTTPStatus.INTERNAL_SERVER_ERROR, error="Problem saving the user's OTP")
            return
    
        if phone_number:
            SmsClient.send_sms_to_pool(SmsTemplate.OTP, user, {"otp": user_verification.otp}, send_now=True)
        else:
            SmtpClient.send_email_to_pool(EmailTemplate.PASSWORD_RECOVERY, user.email, {"otp": user_verification.otp}, send_now=True)
    
        self.response(resp, HTTPStatus.OK, message="OTP sent successfully")

    def __validate_code(self, req: Request, resp: Response):
        data: dict = self.get_req_data(req, resp)
        if not data:
            return

        otp = data.get("otp")
        if not otp:
            self.response(resp, HTTPStatus.BAD_REQUEST, message="otp needed")
            return

        user_verification = UserVerification.get(UserVerification.otp == otp)
        if not user_verification:
            self.response(resp, HTTPStatus.UNAUTHORIZED, message="Incorrect code")
            return

        if not Utils.validate_expiration_time(user_verification.otp_time, "otp"):
            self.response(resp, HTTPStatus.UNAUTHORIZED, message="code expired")
            return

        device_uuid = data.get("device_uuid", "unknown")
        user_verification.otp = None
        user_verification.otp_time = None
        if not user_verification.save():
            self.response(resp, HTTPStatus.INTERNAL_SERVER_ERROR, self.PROBLEM_SAVING_TO_DB)
            return

        session, token = Authenticator.login_by_otp(user_verification.user, device_uuid)
        data = {
            "Bearer": token,
            "session": Utils.serialize_model(session, recursive=True, recursiveLimit=3, blacklist=["device"])
        }
        self.response(resp, HTTPStatus.OK, data, message="Session started")

    @falcon.before(Hooks.post_validations, required_attributes={"new_password": str})
    def on_post_change_password(self, req: Request, resp: Response):
        data = req.media
        session = self.get_session(req, resp)
        if not session:
            return
        
        user: User = session.user
        user.password = str(data["new_password"]) + user.salt
        if not user.save():
            self.response(resp, HTTPStatus.INTERNAL_SERVER_ERROR, self.PROBLEM_SAVING_TO_DB)
            return

        self.response(resp, HTTPStatus.OK, message="Password changed successfully")

    @Decorators.no_authorization_needed
    def on_post(self, req: Request, resp: Response, action: str):
        self.actions[action](req, resp)
