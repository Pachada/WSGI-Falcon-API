from core.Model import *
from core.Utils import Utils
from models.EmailTemplate import EmailTemplate
from models.Status import Status


class EmailSent(Base, Model):
    __tablename__ = "email_sent"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(100), nullable=False)
    code = Column(String(45), nullable=False)
    content = Column(Text, nullable=False)
    created = Column(DateTime, default=Utils.time())
    template_id = Column(BigInteger, ForeignKey(EmailTemplate.id), nullable=False)
    status_id = Column(BigInteger, ForeignKey(Status.id), nullable=False)

    template = relationship(EmailTemplate)
    status = relationship(Status)

    formatters = {"created": Utils.date_formatter}
