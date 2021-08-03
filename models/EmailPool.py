from core.Model import *
from core.Utils import Utils
from models.EmailTemplate import EmailTemplate
from models.Status import Status


class EmailPool(Base, Model):
    __tablename__ = "email_pool"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(100), nullable=False)
    subject = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    send_time = Column(DateTime, default=Utils.time())
    send_attemps = Column(mysql.TINYINT(1), default=0)
    created = Column(DateTime, default=Utils.time())
    updated = Column(DateTime, default=Utils.time(), onupdate=Utils.time())
    status_id = Column(BigInteger, ForeignKey(Status.id), default=Status.PENDING)
    template_id = Column(BigInteger, ForeignKey(EmailTemplate.id), nullable=False)

    template = relationship(EmailTemplate)
    status = relationship(Status)

    formatters = {"created": Utils.date_formatter, "send_time": Utils.date_formatter}
