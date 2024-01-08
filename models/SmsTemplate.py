from core.Model import *


class SmsTemplate(Base, Model):
    # Templates                  #Data
    OTP = 1  # {{otp}}

    __tablename__ = "sms_template"
    __autoload_with__ = engine

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str]
    description: Mapped[str]
    message: Mapped[str]
    created: Mapped[datetime] = mapped_column(default=func.now())
    updated: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    enable: Mapped[bool] = mapped_column(default=True)
