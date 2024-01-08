from core.Model import *
from core.Utils import Utils
from models.NewsType import NewsType
from models.User import User
from models.File import File


class News(Base, Model):
    __tablename__ = "news"
    __autoload_with__ = engine

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id = mapped_column(BigInteger, ForeignKey(User.id))
    file_id_image = mapped_column(BigInteger, ForeignKey(File.id))
    file_id_thumbnail = mapped_column(BigInteger, ForeignKey(File.id))
    type_id = mapped_column(BigInteger, ForeignKey(NewsType.id))
    title = mapped_column(String(100), nullable=False)
    body = mapped_column(String(1000), nullable=False)
    created: Mapped[datetime] = mapped_column(default=func.now())
    updated: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    startdate = mapped_column(DateTime, default=datetime.utcnow())
    enddate = mapped_column(DateTime, default=datetime.utcnow())
    enable: Mapped[bool] = mapped_column(default=True)

    user: Mapped[User] = relationship(User)
    file = relationship(File, foreign_keys=file_id_image)
    thumbnail = relationship(File, foreign_keys=file_id_thumbnail)
    type = relationship(NewsType)
