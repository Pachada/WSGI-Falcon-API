from core.Model import *


class Role(Base, Model):
    # Roles
    ADMIN = 1
    USER = 2
    IMAGES = 3

    __tablename__ = "role"
    __autoload_with__ = engine

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str]
    created: Mapped[datetime] = mapped_column(default=func.now())
    updated: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    enable: Mapped[bool] = mapped_column(default=True)

# Role access
role_access: dict[int, set[str]] = {
    Role.ADMIN: {},
    Role.USER: {},
    Role.IMAGES: {
        "FileLocalController",
        "FileS3Controller"
    }
}