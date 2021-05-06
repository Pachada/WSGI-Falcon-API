from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, DateTime, Date,Text, Float, CHAR, SmallInteger, func, distinct
from sqlalchemy import or_, and_
from sqlalchemy.orm import relationship, exc
from sqlalchemy.sql import func
from sqlalchemy.dialects import mysql
from datetime import datetime
from core.database import Base, db_session as DB

class Model():

    @classmethod
    def get(self, value, filter=None, deleted=False, join=None, with_for_update=False):
        query = DB.query(self)
        if not deleted and "enable" in self.__table__.columns.keys():
            query = query.filter_by(enable=1)
        if filter is not None:
            query = query.filter(filter)
        if isinstance(value, int):
            query = query.filter_by(id=value)
        else:
            query = query.filter(value)
        if with_for_update:
            return query.with_for_update().first()
        else:
            return query.first()

    @classmethod
    def getAll(self, filter=None, limit=None, offset=None, orderBy=None, deleted=False, join=None):
        query = DB.query(self)
        if join:
            if isinstance(join, list):
                for model in join:
                    query = query.join(model)
            else:
                query = query.join(join)
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

    def count(self, filter=None, deleted=False, join=None):
        try:
            query = DB.query(self)
            if join:
                for model in join:
                    query = query.join(model)
            if not deleted and "enable" in self.__table__.columns.keys():
                query = query.filter(self.enable == 1)
            if filter is not None:
                return query.filter(filter).count()
            else:
                return query.count()
        except Exception as exc:
            print(exc)
            return False

    def sum(self, field, filter=None):
        try:
            if field and hasattr(self, field):
                field_ = getattr(self, field, None)
            query = DB.query(func.sum(field_))
            if filter is not None:
                query = query.filter(filter)
            result = query.scalar()
            if not result:
                result = 0
            return result
        except Exception as exc:
            print(exc)
            return False

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

    def min(self, field, filter=None):
        try:
            if field and hasattr(self, field):
                field_ = getattr(self, field, None)
            query = DB.query(func.min(field_))
            if filter is not None:
                query = query.filter(filter)

            return query.scalar()
        except Exception as exc:
            print(exc)
            return False

    @classmethod
    def distinct(self, field, filter=None, deleted=False):
        try:
            if field and hasattr(self, field):
                field_ = getattr(self, field, None)
            query = DB.query(field_)
            if not deleted and "enable" in self.__table__.columns.keys():
                query = query.filter(self.enable == 1)
            if filter is not None:
                query = query.filter(filter)

            return query.distinct().all()
        except Exception as exc:
            print(exc)
            return False

    @staticmethod
    def saveAll(instances):
        try:
            if isinstance(instances, list):
                DB.add_all(instances)
                DB.commit()
            else:
                instances.save()
            return True
        except Exception as exc:
            DB.rollback()
            print("[ERROR-SAVING-ALL]")
            print(exc)
            return False

    @staticmethod
    def remove(instance):
        try:
            DB.expunge(instance)
            return True
        except Exception as exc:
            DB.rollback()
            print("[ERROR-EXPUNGE]")
            print(exc)
            return False