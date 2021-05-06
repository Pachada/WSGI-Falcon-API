from core.Model import *
from core.Utils import Utils
from models.User import User
from models.Device import Device

class Session(Base, Model):
    __tablename__ = 'session'

    id = Column(Integer, primary_key = True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    device_id = Column(Integer, ForeignKey(Device.id), nullable=False)
    token = Column(String(120), nullable=False)
    created = Column(DateTime, default = Utils.time())
    updated = Column(DateTime, default = Utils.time(), onupdate =  Utils.time())
    enable = Column(mysql.TINYINT(1), default=1)

    device = relationship(Device)
    user = relationship(User)

    formatters = {
        "created": Utils.date_formatter,
        "updated": Utils.date_formatter
    }
