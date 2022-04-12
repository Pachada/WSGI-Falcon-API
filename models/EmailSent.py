from core.Model import *
from models.EmailTemplate import EmailTemplate
from models.User import User


class EmailSent(Base, Model):
    __tablename__ = "email_sent"
    __autoload_with__ = engine

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey(User.id), default=None)
    template_id = Column(BigInteger, ForeignKey(EmailTemplate.id), nullable=False)
    content = Column(Text, nullable=False)
    created = Column(DateTime, default=Utils.time())

    template = relationship(EmailTemplate)
    user = relationship(User)

