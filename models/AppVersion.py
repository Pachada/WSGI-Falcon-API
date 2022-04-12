from core.Model import *


class AppVersion(Base, Model):
    __tablename__ = "app_version"
    __autoload_with__ = engine

    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(Float, nullable=False)
    created = Column(DateTime, default=Utils.time())

    @staticmethod
    def get_actual_version():
        return AppVersion.max("version")

    @staticmethod
    def get_actual_version_class():
        return AppVersion.get(AppVersion.max("id"))
