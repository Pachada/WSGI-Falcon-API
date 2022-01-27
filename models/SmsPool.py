from core.Model import *
from core.Utils import Utils
from models.SmsTemplate import SmsTemplate
from models.Status import Status
from models.User import User


class SmsPool(Base, Model):
    __tablename__ = "sms_pool"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey(User.id), nullable=False)
    template_id = Column(BigInteger, ForeignKey(SmsTemplate.id), nullable=False)
    status_id = Column(BigInteger, ForeignKey(Status.id), default=Status.PENDING)
    message = Column(String(160), nullable=False)
    send_time = Column(DateTime, default=Utils.time())
    send_attemps = Column(mysql.TINYINT(1), default=0)
    created = Column(DateTime, default=Utils.time())
    updated = Column(DateTime, default=Utils.time(), onupdate=Utils.time())
    
    template = relationship(SmsTemplate)
    status = relationship(Status)
    user = relationship(User)

    formatters = {
        "created": Utils.date_formatter, 
        "updated": Utils.date_formatter,
        "send_time": Utils.date_formatter
        }
