from core.Model import *
from core.Utils import Utils
from models.User import User

class Device(Base, Model):
    __tablename__ = 'device'

    id = Column(BigInteger, primary_key = True, autoincrement=True)
    uuid = Column(String(300), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    token = Column(String(100), default=None)
    created = Column(DateTime, default = Utils.time())
    updated = Column(DateTime, default = Utils.time(), onupdate =  Utils.time())
    enable = Column(mysql.TINYINT(1), default=1)
    
    user = relationship(User)

    formatters = {
        "created": Utils.date_formatter,
        "updated": Utils.date_formatter
    }
