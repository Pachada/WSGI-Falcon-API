from datetime import date, datetime, timedelta, timezone
from dateutil.parser import parse
import string
import re
import random
import configparser
import pytz
import hashlib
import os
import base64
import logging

def timetz(*args):
    return datetime.now(pytz.timezone("UTC")).timetuple()
    # return datetime.now(pytz.timezone("America/Mexico_City")).timetuple()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [ %(levelname)s ]: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logging.Formatter.converter = timetz
logger = logging.getLogger(__name__)

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
        return Utils.change_datetime_timezone_to_utc0(today) if as_utc0 else today

    @staticmethod
    def string_to_datetime(date: str):
        return parse(date)

    @staticmethod
    def change_datetime_timezone_from_utc0_to_another(date=None, tz_to_change="America/Mexico_City"):
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
        SQLAClhemy receives a function and executes it.
        """
        return lambda: datetime.now(timezone.utc)

    @staticmethod
    def serialize_model(object, recursive=False, formatters=None, recursiveLimit=2, blacklist = None, attributes_blacklist = None):
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
        if blacklist is None:
            blacklist = getattr(object, 'blacklist', set())
        if attributes_blacklist is None:
            attributes_blacklist = getattr(object, 'attributes_blacklist', set())
        if formatters is None:
            formatters = getattr(object, "formatters", object.get_formatters())
        for c in object.__table__.columns.keys():
            if c == "password" or c in attributes_blacklist:
                continue
            value = getattr(object, str(c))
            if c in formatters and value:
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
    def generate_salt(length: int = 6):
        return "".join(random.choice(string.printable) for _ in range(length))

    @staticmethod
    def generate_otp(length: int):
        letters = list(string.ascii_uppercase)
        numbers = list(string.digits)
        exclude = {"I", "O"}
        characters = [i for i in (letters + numbers) if i not in exclude]
        return "".join(random.choice(characters) for _ in range(length))

    @staticmethod
    def validate_expiration_time(otp_time: datetime, config_row="otp"):
        """
        Validates if the otp_time has not expired
        compare to the expiration time of the config_row in the config.ini file

        Parameters
        ----------
        otp_time: `datetime`
                datetime the otp was created

        config_row: `str`
                row in config.ini file

        Returns
        -------
        `bool`
            True if otp_time is still valid, False otherwise.
        """
        config = configparser.ConfigParser()
        config.read(Utils.get_config_ini_file_path())
        otp_expiration_time = int(config.get("EXPIRATION_TIMES", config_row))
        delta = datetime.now(timezone.utc) - otp_time.replace(tzinfo=timezone.utc)
        return delta.total_seconds() / 60 < otp_expiration_time

    @staticmethod
    def check_if_valid_email(email: str):
        """
        Validates that the email address is a valid one using regex
        """
        regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        return bool(re.search(regex, email))
    
    @staticmethod
    def check_if_valid_ten_digits_number(number: str):
        """
        Validates thatnumber is a 10 digit one  using regex
        """
        regex = r"\d{10}"
        return bool(re.search(regex, number))

    @staticmethod
    def generate_token(nbytes=32):
        tok = os.urandom(nbytes)
        return base64.urlsafe_b64encode(tok).rstrip(b"=").decode("ascii")

    @staticmethod
    def get_start_date_and_end_date(start_date=None, end_days=15):
        if not end_days:
            end_days = 15

        if not start_date:
            startdate = datetime.now(timezone.utc)

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
                startdate = datetime.now(timezone.utc)

        enddate = startdate + timedelta(days=end_days)

        return startdate, enddate
