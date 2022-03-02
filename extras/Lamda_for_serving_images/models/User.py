from core.Model import *
from core.Utils import Utils
from models.Role import Role
from models.Person import Person
from models.File import File
from models. App_Version import App_Version

class User(Base, Model):

    __tablename__ = 'users'
    
    id = Column(Integer, primary_key = True, autoincrement=True)
    role_id = Column(Integer, ForeignKey(Role.id), default = Role.USER)
    name = Column(String(191), nullable=False) # Esta información va en Person
    last_name = Column(String(191)) # Esta información va en Person
    nickname = Column(String(50), default=None)
    phone = Column(String(15), default=None)
    email = Column(String(100), nullable=False)
    file_id_avatar = Column(Integer, ForeignKey(File.id), default=2)
    birthday = Column(DateTime, default=None) # Esta información va en Person
    diamonds = Column(Integer, default=0)
    tokens = Column(Integer, default=0)

    password = Column(String(300), nullable=False)
    external_id = Column(Text)
    created_at = Column(DateTime, default = Utils.time())
    updated_at = Column(DateTime, default = Utils.time(), onupdate =  Utils.time())
    version = Column(Float, default = App_Version.get_actual_version_value)
    fb_connect = Column(mysql.TINYINT(1), default=0)
    person_id = Column(Integer, ForeignKey(Person.id), default = None)
    enable = Column(Boolean, default=True)

    # Verificaciones
    verified = Column(mysql.TINYINT(1), default=0) # Ya se verifico su UserVerification
    confirmed_email = Column(mysql.TINYINT(1), default=0)
    confirmed_phone = Column(mysql.TINYINT(1), default=0)

    # OTP
    email_confirmation_code = Column(String(6), default=None)
    email_confirmation_code_time = Column(DateTime, default=None)
    balance_otp = Column(String(6), default=None)
    balance_otp_time = Column(DateTime, default=None)
    otp = Column(String(6), default=None)
    otp_time = Column(DateTime, default=None)
    sms_otp = Column(String(6), default=None)
    sms_otp_time = Column(DateTime, default=None)

    # Fase dos
    verified = Column(mysql.TINYINT(1), default=0)
    is_subscriber = Column(mysql.TINYINT(1), default=0)
    subscriber_until = Column(DateTime, default=None)
    balance = Column(Integer, default=0)
    invitation_code = Column(String(7), default=None)
    
    role = relationship(Role)
    person = relationship(Person)
    file = relationship(File)

    formatters = {
        "birthday": Utils.date_formatter,
        "created_at": Utils.date_formatter,
        "updated_at": Utils.date_formatter,
        "otp_time": Utils.date_formatter,
        "subscriber_until": Utils.date_formatter,
        "email_confirmation_code_time": Utils.date_formatter,
        "balance_otp_time": Utils.date_formatter,
        "sms_otp_time" : Utils.date_formatter
    }

    attributes_blacklist = {
        "role_id", "file_id_avatar", "birthday", "diamonds", "tokens", "email_confirmation_code", "email_confirmation_code_time",
        "external_id", "created_at", "updated_at", "version", "fb_connect", "balance_otp", "balance_otp_time", "person_id", "otp",
        "otp_time", "enable", "invitation_code", "sms_otp", "sms_otp_time"
    }

    def __repr__(self):
        return f'{self.nickname}'


