from core.Model import *
from models.Role import Role


class PasswordType(String):
    def bind_processor(self, dialect):
        def process(value):
            return Utils.get_hashed_string(value)
        return process


class User(Base, Model):
    __tablename__ = "user"
    __autoload_with__ = engine

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str]
    password: Mapped[str] = mapped_column(PasswordType)
    salt: Mapped[Optional[str]]
    email: Mapped[str]
    phone: Mapped[Optional[str]]
    role_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Role.id), default=Role.USER)
    created: Mapped[datetime] = mapped_column(default=func.now())
    updated: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    enable: Mapped[bool] = mapped_column(default=True)

    # Person
    first_name: Mapped[str]
    last_name: Mapped[str]
    birthday: Mapped[date]

    # Verifications
    verified: Mapped[bool] = mapped_column(default=False)
    email_confirmed: Mapped[bool] = mapped_column(default=False)
    phone_confirmed: Mapped[bool] = mapped_column(default=False)

    role: Mapped[Role] = relationship(Role)

    attributes_blacklist = {"salt"}

    def __repr__(self):
        return f"{self.username}, {self.email}"

    @staticmethod
    def check_if_user_exists(username, email):
        if username:
            if check_username := User.get(User.username == username):
                return True, "This username already exists"

        if email:
            if check_email := User.get(User.email == email):
                return True, "This email already has an account"

        return False, ""
