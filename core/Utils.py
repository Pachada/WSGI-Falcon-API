from datetime import time, date, datetime, timedelta
from dateutil.parser import parse
import string
import re
from random import randint
import configparser
import pytz
import hashlib
import os


class Utils:
    @staticmethod
    def get_config_ini_file_path():
        thisfolder = os.path.dirname(os.path.abspath(__file__))
        parent_folder = os.path.abspath(os.path.join(thisfolder, os.pardir))
        return os.path.abspath(os.path.join(parent_folder, "config.ini"))

    @staticmethod
    def today_in_tz(timezone="America/Mexico_City", zero_time=False, as_utc0=False):
        today = datetime.now(pytz.timezone(timezone))
        if zero_time:
            today = today.replace(hour=0, minute=0, second=0)
        if as_utc0:
            return Utils.change_datetime_timezone_to_utc0(today)
        return today

    @staticmethod
    def string_to_datetime(date: str):
        return parse(date)

    @staticmethod
    def change_datetime_timezone_from_utc0_to_another(
        date=None, tz_to_change="America/Mexico_City"
    ):
        """
        Changes date with timezone UTC-0 to America/Mexico_City time

        Parameters
        ----------
        value : `date or datetime`
                Value to changes its location

        Returns
        -------
        `datetime`
            datetime with new timezone
        """
        if not date:
            return

        if isinstance(date, str):
            date = Utils.string_to_datetime(date)

        if not date.tzinfo:
            date = pytz.utc.localize(date)

        return date.astimezone(pytz.timezone(tz_to_change))

    @staticmethod
    def change_datetime_timezone_to_utc0(date=None, date_tz="America/Mexico_City"):
        """
        Changes date to UTC-0 timezone

        Parameters
        ----------
        value : `date or datetime`
                Value to changes its location

        Returns
        -------
        `datetime`
            datetime with new timezone
        """
        if not date:
            return

        if isinstance(date, str):
            date = Utils.string_to_datetime(date)

        # Transfor the datetime object with time zone America/Mexico_City to UTC0
        if not date.tzinfo:
            date = pytz.timezone(date_tz).localize(date)

        return date.astimezone(pytz.utc)

    @staticmethod
    def date_formatter(value):
        """
        Return a string representation of a date

        Parameters
        ----------
        value : `date or datetime`
                value to return as string

        Returns
        -------
        `str`
            The str representation of date.
        """
        if isinstance(value, date) and not isinstance(value, datetime):
            value = datetime(value.year, value.month, value.day)

        today = Utils.today_in_tz()
        if (
            isinstance(value, datetime)
            and value.hour == 0
            and value.minute == 0
            and value.second == 0
            and value.day == today.day
        ):
            return value.isoformat(timespec="seconds")

        if not isinstance(value, datetime):
            return value

        local_time = Utils.change_datetime_timezone_from_utc0_to_another(value)
        return local_time.isoformat(timespec="seconds")

    @staticmethod
    def get_hashed_string(data: str) -> str:
        """
        return the sha256 hash of a string

        Parameters
        ----------
        data : `str`
                Value to get its hash

        Returns
        -------
        `str`
            Hash of the data
        """
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    @staticmethod
    def time():
        """
        Return the current utc0 time function
        Used for creating the models time.
        SQLAClhemy recibes a function and execute it.

        """
        return datetime.utcnow

    @staticmethod
    def serialize_model(
        object,
        recursive=False,
        formatters=None,
        recursiveLimit=3,
        blacklist=[],
        attributes_blacklist=[],
    ):
        """
        Take an object that can be a model instance or a model instances list
        and serialize it in a dictionary recursively, which means that serialization
        will contain model relations. Recursive serilization limit is given by *recursiveLimit*.

        Parameters
        ----------
        object : `instance or instances list`
                A model instance or a model instance list.
        recursive : `bool`
                Indicator if the serializeModel method is or not recursive, False by default.
        formatters : `dict`
                A dictionary with functions to apply on specific model fields in serialize process.
        translator : `function reference`
                A reference of translate function, None by default.
        recursiveLimit : `int`
                The limit of recursion, 3 by default.
        blacklist : `list`
                A list of model relations to avoid in serialize model.
        attributes_blacklist : `list`
                A list of model attributes to avoid in serialize model

        Returns
        -------
        `dict`
            A dictionary with serialized data."""
        if not object:
            if isinstance(object, list):
                return []
            return

        if isinstance(object, list):
            return [
                Utils.serialize_model(
                    item,
                    recursive,
                    formatters,
                    recursiveLimit=recursiveLimit,
                    blacklist=blacklist,
                    attributes_blacklist=attributes_blacklist,
                )
                for item in object
            ]

        result = {}
        if formatters is None:
            formatters = getattr(object, "formatters", {})
        for c in object.__table__.columns.keys():
            if c == "password" or c in attributes_blacklist:
                continue
            value = getattr(object, str(c))
            if c in formatters:
                value = formatters[c](value)
            result[c] = value
        if recursive and recursiveLimit > 1:
            limit = recursiveLimit - 1
            for relation in object.__mapper__.relationships.keys():
                if relation not in blacklist:
                    recursiveObj = getattr(object, relation)
                    blacklistModel = getattr(recursiveObj, "blacklist", blacklist)
                    result[relation] = Utils.serialize_model(
                        recursiveObj,
                        recursive,
                        recursiveLimit=limit,
                        blacklist=blacklistModel,
                    )

        return result

    @staticmethod
    def float_formatter(value):
        """
        Take a *value* and return the value formatted into a float with two decimals,
        if the value is not a basestring instance, then return the same value without float format.

        Parameters
        ----------
        value : `int, float or string`
                Value to return into float format.

        Returns
        -------
        `float`
            A number with float format.
        """
        if isinstance(value, (float, str, int)):
            return "{0:.2f}".format(value)
        else:
            return value

    @staticmethod
    def generate_otp(length):
        exclude = ["I", "O"]
        letters = list(string.ascii_uppercase)
        numbers = [i for i in range(10)]
        letters.extend(numbers)
        otp = ""
        while len(otp) < length:
            index = randint(0, 35)
            letter_to_add = letters[index]
            if letter_to_add not in exclude:
                otp += str(letter_to_add)
        return otp

    @staticmethod
    def validate_otp(user):
        """
        Validates if the otp_time of a user has not expired

        Parameters
        ----------
        user: `User`
                user to check its otp time

        Returns
        -------
        `bool`
            True if otp_time is still valid, False otherwise.
        """
        config = configparser.ConfigParser()
        config.read(Utils.get_config_ini_file_path())
        otp_expiration_time = int(config.get("EXPIRATION_TIMES", "otp"))
        delta = datetime.utcnow() - user.otp_time
        return delta.total_seconds() / 60 < otp_expiration_time

    @staticmethod
    def validate_email_code(user):
        """
        Validates if the email time of a user has not expired

        Parameters
        ----------
        user: `User`
                user to check its email time

        Returns
        -------
        `bool`
            True if email_time is still valid, False otherwise.
        """
        config = configparser.ConfigParser()
        config.read(Utils.get_config_ini_file_path())
        email_confirmation_code_expiration_time = int(
            config.get("EXPIRATION_TIMES", "email_code")
        )
        delta = datetime.utcnow() - user.email_confirmation_code_time
        return delta.total_seconds() / 60 < email_confirmation_code_expiration_time

    @staticmethod
    def validate_session(session):
        """
        Validates if a sessions is valid

        Parameters
        ----------
        session: `Session`
                Session to check

        Returns
        -------
        `bool`
            True if session is still valid, False otherwise.
        """
        config = configparser.ConfigParser()
        config.read(Utils.get_config_ini_file_path())
        session_expiration_time = int(config.get("EXPIRATION_TIMES", "session"))
        token = session.token
        if token is not None:
            delta = datetime.utcnow() - session.updated
            return delta.total_seconds() / 60 < session_expiration_time
        return False

    @staticmethod
    def check_if_valid_email(email):
        regex = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$"
        return bool(re.search(regex, email))

    @staticmethod
    def get_start_date_and_end_date(start_date=None, end_days=15):
        if not end_days:
            end_days = 15

        if not start_date:
            startdate = datetime.utcnow()

        else:
            startdate_formated = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S")
            startdate = Utils.get_datetime_from_utc6_to_utc0(start_date)

            # If it only has the date but not hours and if it is the same day as today: the stardate is utcnow.
            # if it has date but not hours and is a different day as today: the startdate is the one sended.
            # if it has date and hour the stardate is the one sended
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            if (
                startdate_formated.hour == 0
                and startdate_formated.minute == 0
                and startdate_formated.second == 0
            ) and today == startdate_formated:
                startdate = datetime.utcnow()

        enddate = startdate + timedelta(days=end_days)

        return startdate, enddate
