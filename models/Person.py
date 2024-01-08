from core.Model import *


class Person(Base, Model):
    __tablename__ = "person"
    __autoload_with__ = engine

    id: Mapped[int]  = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    birthday: Mapped[date]
    created: Mapped[datetime] = mapped_column(default=func.now())
    updated: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    enable: Mapped[bool] = mapped_column(default=True)
