from core.Model import *
from core.Utils import Utils

class NewsType(Base, Model):
    #New Types
    NEWS_TYPES = {
        "Recordatorio": 1,
        "Aviso": 2, 
        "Comunicado general": 3,
        "Urgente": 4, 
        "Dato curioso": 5
    }

    __tablename__ = 'newstypes'

    id = Column(BigInteger, primary_key = True, autoincrement=True)
    type = Column(String(50), nullable=False)
    enable = Column(mysql.TINYINT(1), nullable=False, default=1)