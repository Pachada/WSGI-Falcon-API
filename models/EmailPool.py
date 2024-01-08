from core.Model import *
from models.EmailTemplate import EmailTemplate
from models.Status import Status


class EmailPool(Base, Model):
    __tablename__ = "email_pool"
    __autoload_with__ = engine

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    email: Mapped[str]
    template_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(EmailTemplate.id))
    status_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Status.id), default=Status.PENDING)
    subject: Mapped[str]
    content: Mapped[str] = mapped_column(Text, deferred=True)  # Lazy load this column
    send_time: Mapped[datetime] = mapped_column(default=func.now())
    send_attemps: Mapped[int] = mapped_column(mysql.TINYINT(1), insert_default=0)
    created: Mapped[datetime] = mapped_column(default=func.now())
    updated: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

    template: Mapped[EmailTemplate] = relationship(EmailTemplate)
    status: Mapped[Status] = relationship(Status)
