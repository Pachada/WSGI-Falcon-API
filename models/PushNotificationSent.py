from core.Model import *
from models.Device import Device
from models.PushNotificationTemplate import PushNotificationTemplate
from models.User import User


class PushNotificationSent(Base, Model):
    __tablename__ = "push_notification_sent"
    __autoload_with__ = engine

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(User.id))
    device_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Device.id), default=None)
    template_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(PushNotificationTemplate.id))
    message: Mapped[str]
    readed: Mapped[int] = mapped_column(mysql.TINYINT(1), default=0)
    created: Mapped[datetime] = mapped_column(default=func.now())
    updated: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

    user: Mapped[User] = relationship(User)
    device: Mapped[Device] = relationship(Device)
