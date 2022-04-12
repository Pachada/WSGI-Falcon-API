from core.Model import *


class Role(Base, Model):
    # Roles
    ROOT = 1
    USER = 2

    __tablename__ = "role"
    __autoload_with__ = engine

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=False)
    created = Column(DateTime, default=Utils.time())
    updated = Column(DateTime, default=Utils.time(), onupdate=Utils.time())
    enable = Column(Boolean, default=1, nullable=False)

