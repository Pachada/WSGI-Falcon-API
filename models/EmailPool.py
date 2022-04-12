from core.Model import *
from models.EmailTemplate import EmailTemplate
from models.Status import Status
from models.User import User


class EmailPool(Base, Model):
    __tablename__ = "email_pool"
    __autoload_with__ = engine

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey(User.id), nullable=False)
    template_id = Column(BigInteger, ForeignKey(EmailTemplate.id), nullable=False)
    status_id = Column(BigInteger, ForeignKey(Status.id), default=Status.PENDING)
    subject = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    send_time = Column(DateTime, default=Utils.time())
    send_attemps = Column(mysql.TINYINT(1), default=0)
    created = Column(DateTime, default=Utils.time())
    updated = Column(DateTime, default=Utils.time(), onupdate=Utils.time())

    template = relationship(EmailTemplate)
    status = relationship(Status)
    user = relationship(User)