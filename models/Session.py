from core.Model import *
from models.User import User
from models.Device import Device


class Session(Base, Model):
    __tablename__ = "session"
    __autoload_with__ = engine

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey(User.id), nullable=False)
    device_id = Column(BigInteger, ForeignKey(Device.id), nullable=False)
    token = Column(String(120), nullable=False)
    created = Column(DateTime, default=Utils.time())
    updated = Column(DateTime, default=Utils.time(), onupdate=Utils.time())
    enable = Column(Boolean, default=True)

    device = relationship(Device)
    user = relationship(User)
