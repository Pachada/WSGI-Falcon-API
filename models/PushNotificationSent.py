from core.Model import *
from core.Utils import Utils
from models.PushNotificationTemplate import PushNotificationTemplate
from models.User import User
from models.Device import Device
from models.Status import Status

class PushNotificationSent(Base, Model):
    __tablename__ = 'pushnotificationsent'

    id = Column(Integer, primary_key = True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id))
    device_id = Column(Integer, ForeignKey(Device.id), default=None)
    template_id = Column(Integer, ForeignKey(PushNotificationTemplate.id))
    status_id = Column(mysql.TINYINT(1), ForeignKey(Status.id))
    ticket = Column(String(200), default=None)
    message = Column(String(200), nullable=False)
    data = Column(String(200)) #JSON
    comments = Column(String(100), default=None)
    read = Column(mysql.TINYINT(1), default=0)
    created = Column(DateTime, default = Utils.time())

    user = relationship(User)
    device = relationship(Device)
    template = relationship(PushNotificationTemplate)
    status = relationship(Status)

    formatters = {
        "created": Utils.date_formatter,
    }

    
