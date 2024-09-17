from core.Model import *
from models.SmsTemplate import SmsTemplate
from models.Status import Status
from models.User import User


class SmsPool(Base, Model):
    __tablename__ = "sms_pool"
    __autoload_with__ = engine

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(User.id), nullable=False)
    template_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(SmsTemplate.id), nullable=False)
    status_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Status.id), default=Status.PENDING)
    message: Mapped[str]
    send_time: Mapped[datetime] = mapped_column(default=func.now())
    send_attemps: Mapped[int] = mapped_column(mysql.TINYINT(1), default=0)
    created: Mapped[datetime] = mapped_column(default=func.now())
    updated: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

    template: Mapped[SmsTemplate] = relationship(SmsTemplate)
    status: Mapped[Status] = relationship(Status)
    user: Mapped[User] = relationship(User)
