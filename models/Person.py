from core.Model import *


class Person(Base, Model):
    __tablename__ = "person"
    __autoload_with__ = engine

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    first_name = Column(String(50), default=None)
    last_name = Column(String(50), default=None)
    birthday = Column(DateTime, default=None)
    created = Column(DateTime, default=Utils.time())
    updated = Column(DateTime, default=Utils.time(), onupdate=Utils.time())
    enable = Column(Boolean, default=True)
