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
from sqlalchemy import or_, and_
from sqlalchemy.orm import relationship, exc
from sqlalchemy.sql import func
from sqlalchemy.dialects import mysql
from sqlalchemy.orm.util import was_deleted, has_identity
from datetime import datetime
from core.database import Base, db_session as DB


class Model:

    """
    The Model Class has methods to process queries in database in a easily way like
    get one, get all, delete and save. The Model class inherits new models.
    """

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
            if s3_file:
                file.delete_file_from_s3(req, resp)
            elif local_file:
                file.delete_file_from_local()

    @classmethod
    def get(self, value, filter=None, deleted=False, join=None, with_for_update=False):
        """
        The get() method can process a query with some parameters to get a response.

        Parameters
        ----------
        value  :  `int`,`str`
                A parameter to filter by.
        filter  :  `str`
                A parameter to filter.
        deleted  :  `bool`
                False by default.
        with_for_update  :  `bool`
                False by default.

        Returns
        ----------
        `object`
            An object with query results."""
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
    def getAll(
        self,
        filter=None,
        limit=None,
        offset=None,
        orderBy=None,
        deleted=False,
        join=None,
    ):
        """
        The getAll() method process a query and returns all found values.

        Parameters
        ----------
        filter : `str`, `int`
            A parameter to filter the query, None by default.
        limit : `int`
            Sets the query limit.
        offset : `str`
            The offset of query.
        orderBy : `str`
            Parameter to order the query.
        deleted : `bool`
            False by default.
        join : `None`
            None by default.

        Returns
        -------
        `object`
            An object with all results.
        """
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
        """
        The soft_delete() method changes the status of a row in deleted column into *deleted* by adding 1,
        this indicate that the row has not been deteled at all but in next queries this row will not be
        taken at least that is specify in the query.

        Returns
        -------
        `bool`
            True if deleted = 1 and save() method processes successful for softDelete(), False otherwise.
        """
        try:
            self.enable = 0
            return self.save()
        except Exception as exc:
            print("[ERROR-SOFT-DELETING]")
            print(exc)
            return False

    def delete(self):
        """
        The delete() method deletes a row from database, if something went wrong
        delete() can roll back changes made too.

        Returns
        -------
        `bool`
            True if delete and commit is process successful, False otherwise.
        """
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
    def delete_multiple(self, filter):
        try:
            query = self.__table__.delete().where(filter)
            DB.execute(query)
            DB.commit()
            return True
        except Exception as exc:
            print(exc)
            return False

    @classmethod
    def count(self, filter=None, deleted=False, join=None):
        """
        The count() method counts all rows depending its parameters wich can be filtered,
        deleted or make a join.

        Parameters
        ----------
        filter : `str`, `int`
            Value to filter by.
        deleted : `bool`
            False by default.
        join : `None`
            None by default.

        Returns
        -------
        `object`
            An object with count() results.
        """
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

    @classmethod
    def sum(self, field, filter=None):
        """
        The sum() method sums all rows of a field, if there is not result then returns 0.

        Parameters
        ----------
        field : `str`
            A string for field of model.
        filter : `None`
            None by default.

        Returns
        -------
        `int`
            Sum of results.
        """
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

    @classmethod
    def max(self, field, filter=None):
        """
        The max() method process a query and returns the max value of a field.

        Parameters
        ----------
        field : `str`
            A string for field of model.
        filter : `None`
            None by default.

        Returns
        -------
        `object`
            An object with max result.
        """
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

    @classmethod
    def min(self, field, filter=None):
        """
        The min() method process a query and returns the min value of a field.

        Parameters
        ----------
        field : `str`
            A string for field of model.
        filter : `None`
            None by default.

        Returns
        -------
        `object`
            An object with min result.
        """
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
        """
        The saveAll() method adds more than one objects of Models and saves them to the database,
        if something went wrong saveAll() can roll back changes made too.

        Parameters
        ----------
        instances : `list`
            A list of instances of model.

        Returns
        -------
        `bool`
            True if add and commit is process successful, False otherwise.
        """
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
        """
        The remove() method removes an instance.

        Parameters
        ----------
        instance : `instance`
            A instance to remove.

        Returns
        -------
        `bool`
            Returns True if the instance is removed, False otherwise.
        """
        try:
            DB.expunge(instance)
            return True
        except Exception as exc:
            DB.rollback()
            print("[ERROR-EXPUNGE]")
            print(exc)
            return False
