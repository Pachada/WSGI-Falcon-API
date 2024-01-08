from core.Model import *


class PushNotificationCatalogue(Base, Model):
    __tablename__ = "push_notification_catalogue"
    __autoload_with__ = engine

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    action: Mapped[str]
