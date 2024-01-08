from sqlalchemy import (
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
    Boolean,
    func,
    distinct
)
from sqlalchemy import or_, and_, select
from sqlalchemy.sql.expression import Select
from sqlalchemy.orm import relationship, exc, mapped_column, Mapped
from sqlalchemy.sql import func
from sqlalchemy.dialects import mysql
from sqlalchemy.orm.util import was_deleted, has_identity
from core.database import Base, engine, db_session as DB
from core.Utils import Utils, datetime, date
from typing import List, Optional


class Model:

    """
    The Model Class has methods to process queries in database in a easily way like
    get one, get all, delete and save. The Model class inherits new models.
    """

    def get_formatters(self):
        return {attribute.name: Utils.date_formatter for attribute in self.__table__.columns if attribute.type.python_type in (datetime, date)}

    def exists_in_database(self):
        """
        Return True if the object exists in database, False otherwise.
        """
        try:
            row = self.get(self.id)
            return row and not was_deleted(self) and has_identity(self)
        except exc.ObjectDeletedError:
            DB.rollback()
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
            if not file:
                continue
            if s3_file:
                file.delete_file_from_s3(req, resp)
            elif local_file:
                file.delete_file_from_local()

    @classmethod
    def get(cls, value, filter=None, deleted=False, join=None, order_by=None):
        """
        The get() method can process a query with some parameters to get a response.

        Parameters
        ----------
        value  :  `int`,`str`
                A parameter to filter by.
        filter  :  `expr`
                A parameter to filter.
        deleted  :  `bool`
                False by default.
        join : `Model`
            A list of model to join the query with. None by default.
        order_by : `expr`
                None by default.
        with_for_update  :  `bool`
                False by default.

        Returns
        ----------
        `object`
            An object with query results."""
        query: Select = select(cls)
        if join:
            if isinstance(join, list):
                for model in join:
                    query = query.join(model)
            else:
                query = query.join(join)
        if not deleted and "enable" in cls.__table__.columns.keys():
            query = query.where(cls.enable == 1)
        if filter is not None:
            query = query.where(filter)
        query = query.where(cls.id == value) if isinstance(value, int) else query.where(value)
        if order_by is not None:
            query = query.order_by(order_by)

        return DB.scalars(query).first()

    @classmethod
    def get_all(cls, filter=None, limit=None, offset=None, order_by=None, deleted=False, join=None, left_join=False, attributes=None):
        """
        The get_all() method process a query and returns all found values.

        Parameters
        ----------
        filter : `str`, `int`
            A parameter to filter the query, None by default.
        limit : `int`
            Sets the query limit.
        offset : `str`
            The offset of query.
        order_by : `str`
            Parameter to order the query.
        deleted : `bool`
            False by default.
        join : `Model`
            A list of model to join the query with. None by default.
        left_join : `bool`
            If the join should be done as left outer join. False by default.
        attributes : `list`
            List of SQLAlchemy column objects to select. Selects all attributes if None.

        Returns
        -------
        `object`
            An object with all results.
        """
        if attributes:
            query: Select = select(*attributes)
        else:
            query: Select = select(cls)
        if join:
            if isinstance(join, list):
                for model in join:
                    query = query.join(model, is_outer=left_join)
            else:
                query = query.join(join, is_outer=left_join)
        if not deleted and "enable" in cls.__table__.columns.keys():
            query = query.where(cls.enable == True)
        if filter is not None:
            query = query.where(filter)
        if order_by is not None:
            if isinstance(order_by, list):
                for ord in order_by:
                    query = query.order_by(ord)
            else:
                query = query.order_by(order_by)
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)

        return DB.scalars(query).all()

    def save(self):
        try:
            DB.add(self)
            DB.flush()
            DB.commit()
            return True
        except Exception as exc:
            DB.rollback()
            print("[ERROR-SAVING]")
            print(exc)
            return False

    def soft_delete(self):
        """
        The soft_delete() method changes the status of a row in the enable column into *deleted* by changing its
        value to 0, this indicate that the row has not been deteled at all but in next queries this row will not be
        taken at least that is specify in the query.

        Returns
        -------
        `bool`
            True if enable = 0 and save() method processes successful for soft_delete(), False otherwise.
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
    def delete_multiple(cls, filter):
        try:
            query = cls.__table__.delete().where(filter)
            DB.execute(query)
            DB.flush()
            DB.commit()
            return True
        except Exception as exc:
            print(exc)
            return False

    @classmethod
    def count(cls, filter=None, deleted=False, join=None):
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
            stmt: Select = select(cls)
            if join:
                if isinstance(join, list):
                    for model in join:
                        stmt = stmt.join(model)
                else:
                    stmt = stmt.join(join)
            if not deleted and "enable" in cls.__table__.columns.keys():
                stmt = stmt.where(cls.enable == 1)
            if filter is not None:
                stmt = stmt.where(filter)
            stmt = select(func.count()).select_from(stmt.subquery())
            return DB.execute(stmt).scalar()
        except Exception as exc:
            print(exc)
            return False

    @classmethod
    def sum(cls, expression, filter=None):
        """
        The `sum` function calculates the sum of a given expression for all rows in a table, applying an optional filter.

        Parameters
        ----------
        expression : `ColumnElement`
            A SQLAlchemy expression representing the value to sum for each row.
        filter : `BinaryExpression`, optional
            A SQLAlchemy expression representing the filter to apply to rows before calculating the sum.

        Returns
        -------
        `float`
            The sum of the values of the given expression for all rows that meet the given filter, or 0 if there are no results.
        """
        try:
            query = select(func.sum(expression))
            if filter is not None:
                query = query.where(filter)
            result = DB.execute(query).scalar()
            return result or 0
        except Exception as exc:
            print(exc)
            return False


    @classmethod
    def max(cls, field, filter=None):
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
            if field and hasattr(cls, field):
                field_ = getattr(cls, field, None)
                query = select(func.max(field_))
                if filter is not None:
                    query = query.where(filter)

                return DB.scalar(query)
        except Exception as exc:
            print(exc)
            return False

    @classmethod
    def min(cls, field, filter=None):
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
            if field and hasattr(cls, field):
                field_ = getattr(cls, field, None)
                query = select(func.min(field_))
                if filter is not None:
                    query = query.where(filter)

                return DB.scalar(query)
        except Exception as exc:
            print(exc)
            return False

    @classmethod
    def distinct(cls, field, filter=None, deleted=False):
        """
        The distinct() method process a query and returns the distinct values of a field.

        Parameters
        ----------
        field : `str`
            A string for field of model.
        filter : `None`
            None by default.
        deleted : `bool`
            False by default.

        Returns
        -------
        `list`
            A list of distinct values.
        """
        try:
            if field and hasattr(cls, field):
                field_ = getattr(cls, field, None)
                query = select(func.distinct(field_))
                if not deleted and "enable" in cls.__table__.columns.keys():
                    query = query.where(cls.enable == True)
                if filter is not None:
                    query = query.where(filter)

                return DB.all(query)
        except Exception as exc:
            print(exc)
            return False

    @staticmethod
    def save_all(instances):
        """
        The save_all() method adds more than one objects of Models and saves them to the database,
        if something went wrong save_all() can roll back changes made too.

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
            if isinstance(instances, (list, tuple)):
                DB.add_all(instances)
                DB.flush()
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
