from core.Model import *


class AppVersion(Base, Model):
    __tablename__ = "app_version"
    __autoload_with__ = engine

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version: Mapped[float] = mapped_column(Float, nullable=False)
    created: Mapped[datetime] = mapped_column(default=func.now())

    @staticmethod
    def get_actual_version():
        return AppVersion.max("version")

    @staticmethod
    def get_actual_version_class():
        return AppVersion.get(AppVersion.max("id"))
