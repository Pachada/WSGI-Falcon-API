from core.Model import *
from core.Utils import Utils
from models.User import User
from models.PushNotificationTemplate import PushNotificationTemplate
from models.Status import Status


class PushNotificationPool(Base, Model):
    __tablename__ = "push_notification_pool"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey(User.id), nullable=False)
    template_id = Column(
        BigInteger, ForeignKey(PushNotificationTemplate.id), nullable=False
    )
    status_id = Column(BigInteger, ForeignKey(Status.id), default=Status.PENDING)
    notification_time = Column(DateTime, default=Utils.time())
    message = Column(String(200), nullable=False)
    data = Column(String(200), default=None)  # JSON/DICT
    ticket = Column(String, default=None)
    send_attemps = Column(mysql.TINYINT(1), default=0)
    created = Column(DateTime, default=Utils.time())
    updated = Column(DateTime, default=Utils.time(), onupdate=Utils.time())
    enable = Column(mysql.TINYINT(1), default=1)

    user = relationship(User)
    template = relationship(PushNotificationTemplate)
    status = relationship(Status)

    formatters = {"created": Utils.date_formatter, "updated": Utils.date_formatter}
