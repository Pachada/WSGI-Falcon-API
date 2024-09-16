import jwt
from typing import Tuple, Optional
import os
from datetime import datetime, timedelta, timezone

class JWTUtils:
    ALGORITHM = "RS256"  # Use RS256 for RSA

    @staticmethod
    def create_token(payload: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Creates a JWT token with the given payload and expiration time.

        :param payload: Payload data for the token.
        :param expires_delta: Optional timedelta for token expiration. If not provided, token will expire in 7 days.
        :return: Encoded JWT token as a string.
        """
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=7)  # Default expiration time of 7 days
        payload["exp"] = expire
        return jwt.encode(payload, JWTUtils._get_private_key(), algorithm=JWTUtils.ALGORITHM)


    @staticmethod
    def verify_token(token: str) -> Tuple[Optional[dict], Optional[str]]:
        """
        Verifies the JWT token and returns the payload if valid, otherwise returns an error message.

        :param token: JWT token to verify.
        :return: Tuple containing either (payload, None) if the token is valid, or (None, error message) if not.
        """
        err = None
        try:
            if token.startswith("Bearer "):
                token = token.split(" ")[1]
            payload = jwt.decode(token, JWTUtils._get_public_key(), algorithms=[JWTUtils.ALGORITHM])
            return payload, err
        except jwt.ExpiredSignatureError as e:
            err = f"Token expired. Get a new one. {e}"
        except jwt.InvalidTokenError as e:
            err = f"Invalid Token. Please pass a valid token. {e}"
        return None, err

    @staticmethod
    def _get_private_key():
        # Key should be in the same folder as this file
        thisfolder = os.path.dirname(os.path.abspath(__file__))
        private_key_path =  os.path.abspath(os.path.join(thisfolder, "private_key.pem"))
        with open(private_key_path, 'r') as key_file:
            return key_file.read()

    @staticmethod
    def _get_public_key():
        # Key should be in the same folder as this file
        thisfolder = os.path.dirname(os.path.abspath(__file__))
        public_key_path =  os.path.abspath(os.path.join(thisfolder, "public_key.pem"))
        with open(public_key_path, 'r') as key_file:
            return key_file.read()