from core.Model import *
from models.SmsTemplate import SmsTemplate
from models.User import User


class SmsSent(Base, Model):
    __tablename__ = "sms_sent"
    __autoload_with__ = engine

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(User.id))
    template_id: Mapped[int]  = mapped_column(BigInteger, ForeignKey(SmsTemplate.id))
    message: Mapped[str] = mapped_column(Text)
    created: Mapped[datetime] = mapped_column(default=func.now())

    template: Mapped[SmsTemplate] = relationship(SmsTemplate)
    user: Mapped[User] = relationship(User)

