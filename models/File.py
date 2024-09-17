from core.Model import *
from models.User import User


class File(Base, Model):
    __tablename__ = "file"
    __autoload_with__ = engine

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    object: Mapped[str]
    size: Mapped[int]
    type: Mapped[str]
    name: Mapped[str]
    hash: Mapped[str]
    is_thumbnail: Mapped[int] = mapped_column(mysql.TINYINT(1), insert_default=0)
    url: Mapped[Optional[str]] # If a file has an url means that the file is publicly available
    is_private: Mapped[bool] = mapped_column(default=False) # If private only the user_who_uploaded and admin can get the file
    user_who_uploaded_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    created: Mapped[datetime] = mapped_column(default=func.now())
    updated: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    enable: Mapped[bool] = mapped_column(default=True)

    user_who_uploaded: Mapped[User] = relationship(User)

    def delete_file_from_s3(self, req, resp):
        logger.info(f"Borrando file: {self.id} del s3")
        from controllers import files3Controller

        files3Controller.on_delete(req, resp, self.id)

    def delete_file_from_local(self, req, resp):
        logger.info(f"Borrando file: {self.id} del local")
        from controllers import filelocalController

        filelocalController.on_delete(req, resp, self.id)
