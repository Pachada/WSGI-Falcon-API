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
    __autoload_with__ = engine

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    type = mapped_column(String(50), nullable=False)
    enable = mapped_column(Boolean, nullable=False, default=1)
