from core.Model import *
from core.Utils import Utils
from models.EmailTemplate import EmailTemplate
from models.User import User


class EmailSent(Base, Model):
    __tablename__ = "email_sent"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey(User.id), default=None)
    template_id = Column(BigInteger, ForeignKey(EmailTemplate.id), nullable=False)
    content = Column(Text, nullable=False)
    created = Column(DateTime, default=Utils.time())
    
    template = relationship(EmailTemplate)
    user = relationship(User)

    formatters = {"created": Utils.date_formatter}
