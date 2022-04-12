from core.Model import *
from core.Utils import Utils
from models.NewsType import NewsType
from models.User import User
from models.File import File


class News(Base, Model):
    __tablename__ = "news"
    __autoload_with__ = engine

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey(User.id))
    file_id_image = Column(BigInteger, ForeignKey(File.id))
    file_id_thumbnail = Column(BigInteger, ForeignKey(File.id))
    type_id = Column(BigInteger, ForeignKey(NewsType.id))
    title = Column(String(100), nullable=False)
    body = Column(String(1000), nullable=False)
    created = Column(DateTime, default=Utils.time())
    updated = Column(DateTime, default=Utils.time(), onupdate=Utils.time())
    startdate = Column(DateTime, default=datetime.utcnow())
    enddate = Column(DateTime, default=datetime.utcnow())
    enable = Column(Boolean, default=True)

    user = relationship(User)
    file = relationship(File, foreign_keys=file_id_image)
    thumbnail = relationship(File, foreign_keys=file_id_thumbnail)
    type = relationship(NewsType)
