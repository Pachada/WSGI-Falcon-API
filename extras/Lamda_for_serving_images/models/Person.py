from core.Model import *
from core.Utils import Utils


class Person(Base, Model):
    __tablename__ = 'person'

    id = Column(Integer, primary_key = True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    birthday = Column(DateTime)
    created = Column(DateTime, default = Utils.time())
    updated = Column(DateTime, default = Utils.time(), onupdate =  Utils.time())
    enable = Column(Boolean, default=True)
    
    formatters = {
        "created": Utils.date_formatter,
        "updated": Utils.date_formatter,
        "birthday": Utils.date_formatter
    }

    @staticmethod
    def new(first_name, last_name, birthday):
        person = Person(
            first_name = first_name,
            last_name = last_name,
            birthday = birthday
        )
        person.save()
        return person

