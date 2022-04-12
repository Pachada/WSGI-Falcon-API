from core.Model import *
from models.PushNotificationTemplate import PushNotificationTemplate
from models.User import User
from models.Device import Device


class PushNotificationSent(Base, Model):
    __tablename__ = "push_notification_sent"
    __autoload_with__ = engine

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey(User.id))
    device_id = Column(BigInteger, ForeignKey(Device.id), default=None)
    template_id = Column(BigInteger, ForeignKey(PushNotificationTemplate.id))
    message = Column(String(200), nullable=False)
    readed = Column(mysql.TINYINT(1), default=0)
    created = Column(DateTime, default=Utils.time())
    updated = Column(DateTime, default=Utils.time(), onupdate=Utils.time())

    user = relationship(User)
    device = relationship(Device)

