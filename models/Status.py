from core.Model import *
from core.Utils import Utils


class Status(Base, Model):
    # STATUS
    PENDING = 1
    PROCESSING = 2
    ERROR = 3
    SEND = 4

    __tablename__ = "status"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    description = Column(String(100), nullable=False)
