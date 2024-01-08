from core.Model import *
from models.PushNotificationCatalogue import PushNotificationCatalogue


class PushNotificationTemplate(Base, Model):
    # Templates                                  #Data

    __tablename__ = "push_notification_template"
    __autoload_with__ = engine

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str]
    description: Mapped[str]
    title: Mapped[str]
    message: Mapped[str]
    private: Mapped[int] = mapped_column(mysql.TINYINT(1), nullable=False)
    catalogue_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(PushNotificationCatalogue.id), nullable=False)
    created: Mapped[datetime] = mapped_column(default=func.now())
    updated: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    enable: Mapped[bool] = mapped_column(default=True)

    catalogue: Mapped[PushNotificationCatalogue] = relationship(PushNotificationCatalogue)
