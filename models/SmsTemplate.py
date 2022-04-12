from core.Model import *


class SmsTemplate(Base, Model):
    # Templates                  #Data
    OTP = 1  # {{otp}}

    __tablename__ = "sms_template"
    __autoload_with__ = engine

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(45), nullable=False)
    description = Column(String(500), nullable=False)
    message = Column(String(160), nullable=False)
    created = Column(DateTime, default=Utils.time())
    updated = Column(DateTime, default=Utils.time(), onupdate=Utils.time())
    enable = Column(Boolean, default=True)
