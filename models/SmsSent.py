from core.Model import *
from core.Utils import Utils
from models.SmsTemplate import SmsTemplate
from models.User import User


class SmsSent(Base, Model):
    __tablename__ = "sms_sent"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey(User.id), default=None)
    template_id = Column(BigInteger, ForeignKey(SmsTemplate.id), nullable=False)
    message = Column(Text, nullable=False)
    created = Column(DateTime, default=Utils.time())
    
    template = relationship(SmsTemplate)
    user = relationship(User)

    formatters = {"created": Utils.date_formatter}
