from core.Model import *


class EmailTemplate(Base, Model):
    # Templates                  #Data
    PASSWORD_RECOVERY = 1  # {{otp}}
    CONFIRM_EMAIL = 2  # {{token}}
    ERROR = 3  # flow, title, description, date, procedure

    __tablename__ = "email_template"
    __autoload_with__ = engine

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(45), nullable=False)
    description = Column(String(500), nullable=False)
    subject = Column(String(100), nullable=False)
    html = Column(Text, nullable=False)
    created = Column(DateTime, default=Utils.time())
    updated = Column(DateTime, default=Utils.time(), onupdate=Utils.time())
    enable = Column(Boolean, default=True)
