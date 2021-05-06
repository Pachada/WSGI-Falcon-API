from datetime import time, date, datetime, timedelta
import string
import re
from random import randint
import configparser
import pytz

class Utils():
    
    @staticmethod
    def time():
        """Return the current utc0 time function"""
        return datetime.utcnow

    @staticmethod
    def serialize_model(object, recursive=False, formatters=None, translator=None, recursiveLimit=3, blacklist=[]):
        if not object:
            if isinstance(object, list):
                return []
            return
        if isinstance(object, list):
            lst = []
            for item in object:
                lst.append(Utils.serialize_model(item, recursive, formatters, recursiveLimit=recursiveLimit, blacklist=blacklist))
            return lst
        else:
            result = {}
            if formatters is None:
                formatters = getattr(object, "formatters", {})
            for c in object.__table__.columns.keys():
                if c == "password":
                    continue
                value = getattr(object, str(c))
                if c in formatters:
                    value = formatters[c](value)
                result[c] = value
            if recursive and recursiveLimit - 1 > 0:
                limit = recursiveLimit - 1
                for relation in object.__mapper__.relationships.keys():
                    if relation not in blacklist:
                        recursiveObj = getattr(object, relation)
                        blacklistModel = getattr(recursiveObj, "blacklist", blacklist)
                        result[relation] = Utils.serialize_model(
                            recursiveObj, recursive, recursiveLimit=limit, blacklist=blacklistModel)
            return result

    @staticmethod
    def date_formatter(value):
        if isinstance(value, date) and not isinstance(value,datetime):
            value = datetime(value.year, value.month, value.day)
            
        if isinstance(value, datetime) and value.hour == 0 and value.minute == 0 and value.second == 0:
            return value.isoformat()

        if isinstance(value, datetime):
            # Fix for the moment to return the time in UTC-6 not UTC-0
            utc_now = pytz.utc.localize(value)
            local_time = utc_now.astimezone(pytz.timezone("America/Mexico_City"))
            return local_time.isoformat()[:-6]
            
        else:
            return value

    @staticmethod
    def float_formatter(value):
        if not isinstance(value, str):
            return '{0:.2f}'.format(value)
        else:
            return value

    @staticmethod
    def generate_otp(length):
        exclude = ["I", "O"]
        letters = list(string.ascii_uppercase)
        numbers = [i for i in range(0,10)]
        letters.extend(numbers)
        otp = ""
        while len(otp) < length:
            index = randint(0,35)
            letter_to_add = letters[index]
            if letter_to_add not in exclude:
                otp += str(letter_to_add)
        return otp

    @staticmethod
    def validate_otp(user):
        config = configparser.ConfigParser()
        config.read('config.ini')
        otp_expiration_time = int(config.get('EXPIRATION_TIMES', 'otp'))
        delta = datetime.utcnow() - user.otp_time
        if (delta.total_seconds()/60) >= otp_expiration_time:
            return False
        return True

    @staticmethod
    def validate_email_code(user):
        config = configparser.ConfigParser()
        config.read('config.ini')
        email_confirmation_code_expiration_time = int(config.get('EXPIRATION_TIMES', 'email_code'))
        delta = datetime.utcnow() - user.email_confirmation_code_time
        if (delta.total_seconds()/60) >= email_confirmation_code_expiration_time:
            return False
        return True

    @staticmethod
    def validate_session(session):
        config = configparser.ConfigParser()
        config.read('config.ini')
        session_expiration_time = int(config.get('EXPIRATION_TIMES', 'session'))
        token = session.token
        if token is not None:
            delta = datetime.utcnow() - session.updated
            if (delta.total_seconds()/60) >= session_expiration_time:
                return False
            return True

        return False    

    @staticmethod
    def check_if_valid_email(email):
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
        if re.search(regex, email):
            return True
        return False

