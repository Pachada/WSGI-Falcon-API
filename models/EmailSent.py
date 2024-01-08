from core.Model import *
from models.EmailTemplate import EmailTemplate


class EmailSent(Base, Model):
    __tablename__ = "email_sent"
    __autoload_with__ = engine

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    email: Mapped[str]
    template_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(EmailTemplate.id))
    content: Mapped[str] = mapped_column(Text, deferred=True)
    created: Mapped[datetime] = mapped_column(default=func.now())

    template: Mapped[EmailTemplate] = relationship(EmailTemplate)
