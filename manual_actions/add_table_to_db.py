from core.database import Base, engine
from models.AppVersion import AppVersion


table_objects = [AppVersion.__table__]

Base.metadata.create_all(engine, tables=table_objects)

