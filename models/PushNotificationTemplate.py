from core.Model import *
from models.PushNotificationCatalogue import PushNotificationCatalogue


class PushNotificationTemplate(Base, Model):
    # Templates                                  #Data

    __tablename__ = "push_notification_template"
    __autoload_with__ = engine

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(String(200), nullable=False)
    private = Column(mysql.TINYINT(1), nullable=False)
    catalogue_id = Column(
        BigInteger, ForeignKey(PushNotificationCatalogue.id), nullable=False
    )
    created = Column(DateTime, default=Utils.time())
    updated = Column(DateTime, default=Utils.time(), onupdate=Utils.time())
    enable = Column(Boolean, default=True)

    catalogue = relationship(PushNotificationCatalogue)
