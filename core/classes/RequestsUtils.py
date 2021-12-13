import requests
from requests.exceptions import HTTPError


class RequestsUtils:
    @staticmethod
    def get_url(url: str, headers=None, response_as_json=True):
        try:
            response = requests.get(url, headers=headers)
            # If the response was successful, no Exception will be raised
            response.raise_for_status()
        except HTTPError as http_err:
            return None, str(http_err)
        except Exception as err:
            return None, str(err)
        if response_as_json:
            return response.json(), None
        else:
            return response, None

    @staticmethod
    def post_url(url: str, data=None, headers=None, response_as_json=True):
        """
        Makes a POST request to the provided url
        """
        try:
            response = requests.post(url, json=data, headers=headers)
            # If the response was successful, no Exception will be raised
            response.raise_for_status()
        except HTTPError as http_err:
            return None, str(http_err)
        except Exception as err:
            return None, str(err)
        if response_as_json:
            return response.json(), None
        else:
            return response, None
