from core.Model import *
from core.Utils import Utils
from models.User import User
from models.App_Version import App_Version

class Device(Base, Model):
    #platform
    PLATFORMS = {
        "ios" : 0,
        "android" : 1
    }
    
    __tablename__ = 'devices'

    id = Column(Integer, primary_key = True, autoincrement=True)
    identifier = Column(String(255), nullable=False)
    platform = Column(String(255), default='unknown')
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    app_version_id = Column(Integer, ForeignKey(App_Version.id), default=1)
    token = Column(String(100), default=None)
    created = Column(DateTime, default = Utils.time())
    updated = Column(DateTime, default = Utils.time(), onupdate =  Utils.time())
    enable = Column(Boolean, default=True)
    
    user = relationship(User)
    version = relationship(App_Version)

    formatters = {
        "created": Utils.date_formatter,
        "updated": Utils.date_formatter
    }
