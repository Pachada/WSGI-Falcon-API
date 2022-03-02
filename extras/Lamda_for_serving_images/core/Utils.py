from datetime import date, datetime, timedelta
import configparser
import pytz
import hashlib
import os

class Utils():

    @staticmethod
    def get_config_ini_file_path():
        thisfolder = os.path.dirname(os.path.abspath(__file__))
        parent_folder = os.path.abspath(os.path.join(thisfolder, os.pardir))
        return os.path.abspath(os.path.join(parent_folder, 'config.ini'))

    @staticmethod
    def get_hashed_string(password:str):
        return hashlib.sha256(password.encode('utf-8')).hexdigest() 

    
    @staticmethod
    def time():
        """
        Return the current utc0 time function
        Used in the datetime columns in the Data Models
        """
        return datetime.utcnow


    @staticmethod
    def serialize_model(object, recursive=False, formatters=None, recursiveLimit=2, blacklist = None, attributes_blacklist=set()):
        if blacklist is None:
            blacklist = []
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
            if c in attributes_blacklist or c == "password" :
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
                        recursiveObj, recursive, recursiveLimit=limit, blacklist=blacklistModel, attributes_blacklist=attributes_blacklist)
        return result


    @staticmethod
    def date_formatter(value):
        """
        Changes date timezone from UTC-0 to UTC-6

        Parameters
        ----------
        value : `date or datetime`
                Value to changes its location

        Returns
        -------
        `str`
            The str representation of date.
        """
        if isinstance(value, date) and not isinstance(value,datetime):
            value = datetime(value.year, value.month, value.day)

        today = datetime.now(pytz.timezone("America/Mexico_City"))
        if isinstance(value, datetime) and value.hour == 0 and value.minute == 0 and value.second == 0 and value.day == today.day:
            return value.isoformat()

        if not isinstance(value, datetime):
            return value

        try:
            # Fix for the moment to return the time in UTC-6 not UTC-0
            utc_now = pytz.utc.localize(value)
            local_time = utc_now.astimezone(pytz.timezone("America/Mexico_City"))
            return local_time.isoformat()[:-6]
        except Exception as exc:
            return value.isoformat()[:-6]

    @staticmethod
    def validate_session(session):
        config = configparser.ConfigParser()
        config.read(Utils.get_config_ini_file_path())
        session_expiration_time = int(config.get('EXPIRATION_TIMES', 'session'))
        token = session.token
        if token is not None:
            delta = datetime.utcnow() - session.updated
            return delta.total_seconds()/60 < session_expiration_time  