from core.Model import *
from core.Utils import Utils

class Role(Base, Model):
    # Roles
    ADMIN = 1
    DUEALZO = 2 # Otro tipo de Admin
    USER = 3 
    
    __tablename__ = 'roles'

    id = Column(Integer, primary_key = True, autoincrement=True)
    name = Column(String(30), nullable=False)
    display_name = Column(String(50))
    created = Column(DateTime, default = Utils.time())
    updated = Column(DateTime, default = Utils.time(), onupdate =  Utils.time())
    enable = Column(Boolean, default=1, nullable=False)

    formatters = {
        "created": Utils.date_formatter,
        "updated": Utils.date_formatter
    }
