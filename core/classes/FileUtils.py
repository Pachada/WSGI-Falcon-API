from falcon.request import Request
from falcon.response import Response
from core.Controller import Controller, json
from core.Utils import Utils
from models.File import File
import configparser
from PIL import Image
import io
import sys
import base64
from falcon.media.multipart import BodyPart
import magic
from abc import ABC, abstractmethod

class FileSizeGraterThanAllowed(Exception):
    """Exception raised for errors in the input salary.

    Attributes:
        salary -- input salary which caused the error
        message -- explanation of the error
    """

    def __init__(self):
        self.message = "El archivo es mayor a 4mb"
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'

class ContentTypeNotAllowed(Exception):
    """Exception raised for errors in the input salary.

    Attributes:
        salary -- input salary which caused the error
        message -- explanation of the error
    """

    def __init__(self, invalid_type, accepted_types):
        self.invalid_type = invalid_type
        self.message = (f"Archivos de tipo {invalid_type} no son permitidos, "
                        f"por favor sube un archivo permitido: {accepted_types}"
                        )
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'

class FileController(Controller):

    CHUNK_SIZE = 8192

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(Utils.get_config_ini_file_path())
        # list of accepted files types
        self.accepted_files = json.loads(self.config.get("FILES", "accepted_files"))
        # Maximum file size accepted
        self.max_file_size = int(self.config.get("FILES", "max_file_size"))
    

    def procces_stream(self, part: BodyPart):
        self.check_if_valid_content_type(part.content_type)

        read_so_far = 0
        data = []
        while chunk := part.stream.read(self.CHUNK_SIZE):
            data.append(chunk)
            read_so_far += len(chunk)
            if read_so_far > self.max_file_size:
                raise FileSizeGraterThanAllowed()
        
        return b''.join(data)

    def on_post(self, req: Request, resp: Response, id: int = None):
        if id:
            self.response(resp, 405)
            return

        make_thumbnail = self.check_if_make_thumbnail(req)
        data = []
        form = req.get_media()
        for part in form: # Only procces the first file
            part: BodyPart = part
            try:
                stream_content = self.procces_stream(part)
            except  Exception as e:
                self.response(resp, 400, error = str(e))
                return

            file_data, thumbnail_data, code = self.procces_file(
                part.filename,
                stream_content,
                part.content_type,
                make_thumbnail=make_thumbnail,
            )
            data.append(file_data)
            if thumbnail_data: data.append(thumbnail_data)
            break

        self.response(resp, code, data)

    def on_post_base64(self, req: Request, resp: Response, id: int = None):
        if id:
            self.response(resp, 405)
            return

        base64_info, file_name, error_message = self.get_base64_info(req)
        if not base64_info:
            self.response(resp, 400, error=error_message)
            return

        base64_decoded = self.decode_base64_file(base64_info)
        mimetype = self.get_mimetype(base64_decoded)

        try:
            self.check_if_valid_content_type(mimetype)
        except ContentTypeNotAllowed as e:
            self.response(resp, 400, error=str(e))
            return

        make_thumbnail = self.check_if_make_thumbnail(req)
        file, thumbnail, code = self.procces_file(
            file_name, base64_decoded, mimetype, make_thumbnail=make_thumbnail
        )
        data = file
        if thumbnail:
            data = [file, thumbnail]

        self.response(resp, code, data)

    def check_if_valid_content_type(self, content_type):
        if content_type not in self.accepted_files:
            raise ContentTypeNotAllowed(content_type, self.accepted_files)

    def check_if_valid_file_size(self, data):
        return sys.getsizeof(data) < self.max_file_size

    def check_if_make_thumbnail(self, req: Request):
        return req.params.get("thumbnail") == "True"        

    def procces_file(
        self, filename, data, content_type, encode_to_base64=False, make_thumbnail=False
    ):

        file = self.create_file( # the create_file method is implemented by the subclasses
            filename,
            data,
            content_type,
            encode_to_base64=encode_to_base64,
        )

        if not file:
            return {"Filename": filename, "Error": self.PROBLEM_SAVING_TO_DB}, None, 500

        thumbnail = None
        if make_thumbnail and (
            "jpeg" in content_type or "png" in content_type or "jpg" in content_type
        ):
            thumbnail = self.create_thumbnail(
                data,
                filename,
                content_type,
                encode_to_base64,
            )
            if not thumbnail:
                thumbnail = {
                    "Filename_thumbnail": filename,
                    "error": self.PROBLEM_SAVING_TO_DB,
                }
            else:
                thumbnail = Utils.serialize_model(thumbnail)

        return Utils.serialize_model(file), thumbnail, 201

    def create_thumbnail(self, image_data, filename, content_type, encode_to_base64):
        thumbnail_content = self.create_thumbnail_image(image_data)
        filename = filename.split(".")
        thumbnail_name = (
            filename[0]
            + "_thumbnail"
            + ("." + filename[1] if len(filename) > 1 else "")
        )
        return self.create_file(  # the create_file method is implemented by the subclasses
            thumbnail_name,
            thumbnail_content,
            content_type,
            is_thumbnail=1,
            encode_to_base64=encode_to_base64,
        )

    def create_thumbnail_image(self, image_data):
        with Image.open(io.BytesIO(image_data)) as image_data_content:
            image_data_content.thumbnail(size=(640, 640))
            b = io.BytesIO()
            if image_data_content.format == "PNG":
                image_data_content.save(b, "PNG")
            elif image_data_content.format == "JPG":
                image_data_content.save(b, "JPG")
            else:
                image_data_content.save(b, "JPEG")
        b.seek(0)
        return b

    def decode_base64_file(self, base64_info):
        return base64.b64decode(base64_info)

    def encode_to_base64(self, data):
        return base64.b64encode(data)

    def get_mimetype(self, data):
        return magic.from_buffer(data, mime=True)
    
    def get_base64_file_length(self, b64string):
        return (len(b64string) * 3) / 4 - b64string.count('=', -1, -5)

    def get_base64_info(self, req: Request):
        try:
            data: dict = json.loads(req.stream.read())
        except Exception as exc:
            return None, None, str(exc)

        file_name = data.get("file_name")
        base64_info: str = data.get("base64")
        if not file_name or not base64_info:
            return None, None, "'file_name' and 'base64' needed"

        if self.get_base64_file_length(base64_info) > self.max_file_size:
            return None, None, f"El archivo {file_name} es mayor a 4mb."
        
        return base64_info, file_name, None

    def format_file_content(self, file_content):
        if isinstance(file_content, str):
            file_content = file_content.encode("utf-8")

        elif not isinstance(file_content, bytes):
            file_content = file_content.read()

        return file_content


class FileAbstract(ABC):
    @abstractmethod
    def create_file(
        self,
        file_name: str,
        file_content,
        file_type,
        is_thumbnail=0,
        encode_to_base64=True
    ):
        pass