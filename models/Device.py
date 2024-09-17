from core.Model import *
from models.AppVersion import AppVersion
from models.User import User


class Device(Base, Model):
    __tablename__ = "device"
    __autoload_with__ = engine

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    uuid: Mapped[str]
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(User.id))
    token: Mapped[Optional[str]]
    app_version_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(AppVersion.id), default=1)
    created: Mapped[datetime] = mapped_column(default=func.now())
    updated: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    enable: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped[User] = relationship(User)
    app_version: Mapped[AppVersion] = relationship(AppVersion)
