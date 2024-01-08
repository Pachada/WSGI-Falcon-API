import configparser
from sqlalchemy import create_engine, exc, event, select
from sqlalchemy.orm import scoped_session, sessionmaker, DeclarativeBase, mapped_column, MappedAsDataclass
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from core.Utils import Utils


Config = configparser.ConfigParser()
Config.read(Utils.get_config_ini_file_path())

host = Config.get("DATABASE", "host")
port = Config.get("DATABASE", "port")
database = Config.get("DATABASE", "database")
user = Config.get("DATABASE", "user")
password = Config.get("DATABASE", "password")

engine = create_engine(
    f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}",
    pool_size=20,
    max_overflow=10,
    pool_recycle=3600,
    pool_timeout=10,
    isolation_level="READ UNCOMMITTED",
    pool_pre_ping=True,
)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

class Base(DeclarativeBase):
    pass


"""@event.listens_for(engine, "engine_connect")
def ping_connection(connection, branch):
    if branch:
        return
    save_should_close_with_result = connection.should_close_with_result
    connection.should_close_with_result = False

    try:
        print(f"ping connection {datetime.now()}")
        connection.scalar(select([1]))
    except exc.DBAPIError as err:
        if err.connection_invalidated:
            connection.scalar(select([1]))
        else:
            raise
    finally:
        connection.should_close_with_result = save_should_close_with_result"""
