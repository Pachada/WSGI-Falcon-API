from core.Model import *
from models.PushNotificationTemplate import PushNotificationTemplate
from models.Status import Status
from models.User import User


class PushNotificationPool(Base, Model):
    __tablename__ = "push_notification_pool"
    __autoload_with__ = engine

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(User.id), default=None)
    template_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(PushNotificationTemplate.id), nullable=False)
    status_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Status.id), default=Status.PENDING)
    send_time: Mapped[datetime] = mapped_column(DateTime, default=Utils.time())
    message: Mapped[str]
    data: Mapped[str]  # JSON/DICT for information on the push
    send_attemps: Mapped[int] = mapped_column(mysql.TINYINT(1), default=0)
    created: Mapped[datetime] = mapped_column(default=func.now())
    updated: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

    user: Mapped[User] = relationship(User)
    template: Mapped[PushNotificationTemplate] = relationship(PushNotificationTemplate)
    status: Mapped[Status] = relationship(Status)
