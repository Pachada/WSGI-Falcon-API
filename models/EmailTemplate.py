from core.Model import *


class EmailTemplate(Base, Model):
    # Templates                  #Data
    PASSWORD_RECOVERY = 1  # {{otp}}
    CONFIRM_EMAIL = 2  # {{token}}
    ERROR = 3  # flow, title, description, date, procedure

    __tablename__ = "email_template"
    __autoload_with__ = engine

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str]
    description: Mapped[str]
    subject: Mapped[str]
    html: Mapped[str] = mapped_column(Text, deferred=True)
    created: Mapped[datetime] = mapped_column(default=func.now())
    updated: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    enable: Mapped[bool] = mapped_column(default=True)
