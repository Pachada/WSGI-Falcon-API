from core.Model import *
from core.Utils import Utils

class App_Version(Base, Model):
    __tablename__ = 'app_version'
    
    id = Column(Integer, primary_key = True, autoincrement=True)
    version = Column(Float, nullable=False)
    created_at = Column(DateTime, default = Utils.time())

    formatters = {
        "created_at": Utils.date_formatter
    }

    @staticmethod
    def get_actual_version_class():
        max_id = App_Version.max("id")
        return App_Version.get(int(max_id))
    
    @staticmethod
    def get_actual_version_value():
        max_id = App_Version.max("id")
        app_version =  App_Version.get(int(max_id))
        return app_version.version