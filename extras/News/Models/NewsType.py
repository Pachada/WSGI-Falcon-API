from core.Model import *
from core.Utils import Utils


class NewsType(Base, Model):
    # New Types
    RECORDATORIO = 1
    AVISO = 2
    COMUNICADO_GENERAL = 3
    URGENTE = 4
    DATOS_CURISOSO = 5

    __tablename__ = "news_types"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    type = Column(String(50), nullable=False)
    enable = Column(mysql.TINYINT(1), nullable=False, default=1)
