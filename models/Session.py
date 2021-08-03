from core.Model import *
from core.Utils import Utils
from models.User import User
from models.Device import Device


class Session(Base, Model):
    __tablename__ = "session"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey(User.id), nullable=False)
    device_id = Column(BigInteger, ForeignKey(Device.id), nullable=False)
    token = Column(String(120), nullable=False)
    created = Column(DateTime, default=Utils.time())
    updated = Column(DateTime, default=Utils.time(), onupdate=Utils.time())
    enable = Column(mysql.TINYINT(1), default=1)

    device = relationship(Device)
    user = relationship(User)

    formatters = {"created": Utils.date_formatter, "updated": Utils.date_formatter}
