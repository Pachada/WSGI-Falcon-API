from core.Model import *
from models.Role import Role
from models.Person import Person


class User(Base, Model):
    __tablename__ = "user"
    __autoload_with__ = engine

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False)
    password = Column(String(300), nullable=False)
    salt = Column(String(6), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(15), default=None)
    role_id = Column(BigInteger, ForeignKey(Role.id), default=Role.USER)
    person_id = Column(BigInteger, ForeignKey(Person.id))
    created = Column(DateTime, default=Utils.time())
    updated = Column(DateTime, default=Utils.time(), onupdate=Utils.time())
    enable = Column(Boolean, default=True)

    # Verifications
    verified = Column(Boolean, default=False)
    email_confirmed = Column(Boolean, default=False)
    phone_confirmed = Column(Boolean, default=False)

    role = relationship(Role)
    person = relationship(Person)

    @staticmethod
    def check_if_user_exists(username, email):
        if username:
            check_username = User.get(User.username == username)
            if check_username:
                return True, "This username already exists"

        if email:
            check_email = User.get(User.email == email)
            if check_email:
                return True, "This email already has an account"

        return False, ""
