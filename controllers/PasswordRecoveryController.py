from core.Controller import Controller, Utils, Request, Response, json, datetime
from core.classes.Authenticator import Authenticator
from models.UserVerification import UserVerification, User
from models.EmailTemplate import EmailTemplate
from core.classes.SmtpClient import SmtpClient
from core.classes.SmsClient import SmsClient, SmsTemplate

class PasswordRecoveryController(Controller):
    def __init__(self):
        self.actions = {
            "request": self.__request,
            "validate-code": self.__validate_code,
            "change-password": self.__change_password,
        }

    def __request(self, req:Request, resp:Response):
        data:dict = self.get_req_data(req, resp)
        if not data: return

        email = data.get('email')
        phone_number = data.get('phone_number')
        if not email and not phone_number:
            self.response(resp, 400, error = "Se necesita el correo o el número telefónico")
            return
        
        if phone_number:
            filter= (User.phone == str(phone_number))
        else:
            filter = (User.email == str(email))

        user = User.get(filter)
        if not user:
            self.response(resp, 404, error = "Usuario no encontrado")
            return
        
        user_verification = UserVerification.get_verification_of_user(user)
        if not user_verification: 
            self.response(resp, 500, error = "Problema con la Verificación del Usuario")
            return

        user_verification.otp = Utils.generate_otp(5)
        user_verification.otp_time = datetime.utcnow()
        if not user_verification.save():
            self.response(resp, 500, error="Problema al guardar el otp del usuario")
            return
        
        if phone_number:
            SmsClient.send_sms_to_pool(SmsTemplate.OTP, user, {"otp": user_verification.otp}, send_now=True)
        else:
            SmtpClient.send_email_to_pool(EmailTemplate.PASSWORD_RECOVERY, user, {"otp": user_verification.otp}, send_now=True)

        self.response(resp, 200, message="OTP enviado satisfactoriamente")

    def __validate_code(self, req: Request, resp: Response):
        data: dict = self.get_req_data(req, resp)
        if not data:
            return

        otp = data.get("otp")
        if not otp:
            self.response(resp, 400, message="otp needed")
            return

        user_verification = UserVerification.get(UserVerification.otp == otp)
        if not user_verification:
            self.response(resp, 401, message="Incorrect code")
            return

        if not Utils.validate_expiration_time(user_verification.otp_time, "otp"):
            self.response(resp, 401, message="code expired")
            return

        device_uuid = data.get("device_uuid", "unknown")
        user_verification.otp = None
        user_verification.otp_time = None
        if not user_verification.save():
            self.response(resp, 500, self.PROBLEM_SAVING_TO_DB)
            return

        session = Authenticator.login_by_otp(user_verification.user, device_uuid)
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

        new_password = data.get("new_password")
        if not new_password:
            self.response(resp, 400, error="new_password is required")
            return

        session = req.context.session
        user: User = session.user

        user.password = Utils.get_hashed_string(str(new_password) + user.salt)
        if not user.save():
            self.response(resp, 500, self.PROBLEM_SAVING_TO_DB)
            return

        self.response(resp, 200, message="Password changed successfully")

    def on_post(self, req: Request, resp: Response, action: str):
        self.actions[action](req, resp)
