from core.Model import *
from models.User import User
from models.AppVersion import AppVersion


class Device(Base, Model):
    __tablename__ = "device"
    __autoload_with__ = engine

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    uuid = Column(String(300), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    token = Column(String(100), default=None)
    app_version_id = Column(BigInteger, ForeignKey(AppVersion.id), default=1)
    created = Column(DateTime, default=Utils.time())
    updated = Column(DateTime, default=Utils.time(), onupdate=Utils.time())
    enable = Column(Boolean, default=True)

    user = relationship(User)
    app_version = relationship(AppVersion)

    formatters = {"created": Utils.date_formatter, "updated": Utils.date_formatter}
