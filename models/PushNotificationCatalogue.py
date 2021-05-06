from core.Model import *
from core.Utils import Utils


class PushNotificationCatalogue(Base, Model):
    __tablename__ = "pushnotificationcatalogue"

    id = Column(Integer, primary_key = True, autoincrement=True)
    action = Column(String(45), nullable=False)