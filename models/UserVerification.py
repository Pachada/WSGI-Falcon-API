from core.Model import *
from models.File import File
from models.Status import Status
from models.User import User


class UserVerification(Base, Model):
    __tablename__ = "user_verification"
    __autoload_with__ = engine

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(User.id), primary_key=True, nullable=False)
    curp: Mapped[Optional[str]]
    status_id_curp: Mapped[int] = mapped_column(BigInteger, ForeignKey(Status.id), default=Status.MISSING)
    file_id_ine: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey(File.id))
    status_id_ine: Mapped[int] = mapped_column(BigInteger, ForeignKey(Status.id), default=Status.MISSING)
    comments: Mapped[Optional[str]]
    updated: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

    # OTP
    otp: Mapped[Optional[str]]
    otp_time: Mapped[Optional[datetime]]
    email_otp: Mapped[Optional[str]]
    email_otp_time: Mapped[Optional[datetime]]
    sms_otp: Mapped[Optional[str]]
    sms_otp_time: Mapped[Optional[datetime]]

    user: Mapped[User] = relationship(User)
    status_curp: Mapped[Status] = relationship(Status, foreign_keys=status_id_curp)
    file_ine: Mapped[File] = relationship(File, foreign_keys=file_id_ine)
    status_ine: Mapped[Status] = relationship(Status, foreign_keys=status_id_ine)

    @staticmethod
    def get_verification_of_user(user: User):

        user_verification = UserVerification.get(UserVerification.user_id == user.id)

        if not user_verification:
            user_verification = UserVerification(user_id=user.id)
            if not user_verification.save():
                return None

        return user_verification
