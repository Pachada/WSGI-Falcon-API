from core.Model import *
from core.Utils import Utils


class EmailTemplate(Base, Model):
    # Templates                  #Data
    PASSWORD_RECOVERY = 1       # {{otp}}
    CONFIRM_EMAIL = 2           # {{email_confirmation_code}}

    __tablename__ = "email_template"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(45), nullable=False)
    subject = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    html = Column(Text, nullable=False)
    created = Column(DateTime, default=Utils.time())
    updated = Column(DateTime, default=Utils.time(), onupdate=Utils.time())
    enable = Column(mysql.TINYINT(1), default=1)

    formatters = {"created": Utils.date_formatter, "updated": Utils.date_formatter}
