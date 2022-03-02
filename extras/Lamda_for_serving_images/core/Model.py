from sqlalchemy import (
    Column,
    Integer,
    String,
    BigInteger,
    ForeignKey,
    DateTime,
    Date,
    Text,
    Float,
    CHAR,
    SmallInteger,
    func,
    distinct,
)
from sqlalchemy import or_, and_, case, MetaData
from sqlalchemy.orm import relationship, exc
from sqlalchemy.sql import func
from sqlalchemy.dialects import mysql
from sqlalchemy.orm.util import was_deleted, has_identity
from datetime import datetime
from core.database import Base, db_session as DB


class Model:
    def exists_in_database(self):
        """
        Return True if the object exists in database, False otherwise.
        """
        try:
            row = self.get(self.id)
            return row and not was_deleted(self) and has_identity(self)
        except exc.ObjectDeletedError:
            return False

    def get_files(self):
        """
        Returns a list with the file objects of a Model subclass
        """
        return [
            getattr(self, relation)
            for relation in self.__mapper__.relationships.keys()
            if "file" in relation
        ]

    def delete_model_files(self, req, resp, s3_file=True, local_file=False):
        """
        The  delete_model_files() delete the files asociated to a model instance using the FileS3Controller
        or the FileLocalController on_delete methods, witch requiere the req and resp.
        Be carefull; if the relatonship with the model is in Cascade, it will delete the row.
        """
        for file in self.get_files():
            if not file: continue
            if s3_file:
                file.delete_file_from_s3(req, resp)
            elif local_file:
                file.delete_file_from_local()

    @classmethod
    def get(self, value, filter=None, deleted=False, join=None, with_for_update=False, order_by=None):
        query = DB.query(self)
        if join:
            if isinstance(join, list):
                for model in join:
                    query = query.join(model)
            else:
                query = query.join(join)
        if not deleted and "enable" in self.__table__.columns.keys():
            query = query.filter_by(enable=1)
        if filter is not None:
            query = query.filter(filter)
        if isinstance(value, int):
            query = query.filter_by(id=value)
        else:
            query = query.filter(value)
        if order_by is not None:
            query = query.order_by(order_by)

        return query.with_for_update().first() if with_for_update else query.first()

    @classmethod
    def getAll(
        self,
        filter=None,
        limit=None,
        offset=None,
        orderBy=None,
        deleted=False,
        join=None,
        left_join=False,
    ):
        query = DB.query(self)
        if join:
            if isinstance(join, list):
                for model in join:
                    query = query.join(model, isouter=left_join)
            else:
                query = query.join(join, isouter=left_join)
        if not deleted and "enable" in self.__table__.columns.keys():
            query = query.filter(self.enable == 1)
        if filter is not None:
            query = query.filter(filter)
        if orderBy is not None:
            if isinstance(orderBy, list):
                for ord in orderBy:
                    query = query.order_by(ord)
            else:
                query = query.order_by(orderBy)
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)
        return query.all()

    def save(self):
        try:
            DB.add(self)
            DB.commit()
            return True
        except Exception as exc:
            DB.rollback()
            print("[ERROR-SAVING]")
            print(exc)
            return False

    def soft_delete(self):
        try:
            self.enable = 0
            return self.save()
        except Exception as exc:
            print("[ERROR-SOFT-DELETING]")
            print(exc)
            return False

    def delete(self):
        try:
            DB.delete(self)
            DB.commit()
            return True
        except Exception as exc:
            DB.rollback()
            print("[ERROR-DELETING]")
            print(exc)
            return False

    @classmethod
    def max(self, field, filter=None):
        try:
            if field and hasattr(self, field):
                field_ = getattr(self, field, None)
            query = DB.query(func.max(field_))
            if filter is not None:
                query = query.filter(filter)

            return query.scalar()
        except Exception as exc:
            print(exc)
            return False
