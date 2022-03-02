from falcon.request import Request
from falcon.response import Response
from core.Controller import Controller, json
from core.Utils import Utils
from models.File import File
import configparser
import base64


class FileController(Controller):
    """
    The FileController class inherits new File controllers classes and
    provide them with common used methods 

    """

    CHUNK_SIZE = 8192

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(Utils.get_config_ini_file_path())
        # list of accepted files types
        self.accepted_files = json.loads(self.config.get("FILES", "accepted_files"))

    def encode_to_base64(self, data):
        return base64.b64encode(data)
