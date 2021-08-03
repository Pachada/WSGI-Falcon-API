from core.Model import *
from core.Utils import Utils


class PushNotificationCatalogue(Base, Model):
    __tablename__ = "push_notification_catalogue"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    action = Column(String(45), nullable=False)
