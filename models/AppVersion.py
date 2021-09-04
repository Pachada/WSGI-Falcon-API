from core.Model import *
from core.Utils import Utils


class AppVersion(Base, Model):
    __tablename__ = 'app_version'
    
    id = Column(Integer, primary_key = True, autoincrement=True)
    version = Column(Float, nullable=False)
    created = Column(DateTime, default = Utils.time())

    formatters = {
        "created": Utils.date_formatter
    }

    @staticmethod
    def get_actual_version():
        return AppVersion.max("version")
    
    @staticmethod
    def get_actual_version_class():
        return AppVersion.get(AppVersion.max("id"))
