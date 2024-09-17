from core.Model import *
from models.Device import Device
from models.User import User


class Session(Base, Model):
    __tablename__ = "session"
    __autoload_with__ = engine

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(User.id))
    device_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Device.id))
    created: Mapped[datetime] = mapped_column(default=func.now())
    updated: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    enable: Mapped[bool] = mapped_column(default=True)

    device: Mapped[Device] = relationship(Device)
    user: Mapped[User] = relationship(User)
