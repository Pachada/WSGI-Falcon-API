import base64
import configparser
import io
import json
import sys
from abc import ABC, abstractmethod

import filetype
from falcon.media.multipart import BodyPart
from PIL import Image

from core.Controller import (ROUTE_LOADER, Controller, Hooks, HTTPStatus,
                             Request, Response, Utils, datetime, falcon, json)
from core.Utils import Utils, logger
from models.File import File, User


class FileSizeGreaterThanAllowed(Exception):
    """Exception raised for errors in file processing"""

    def __init__(self):
        self.message = "The file size exceeds the allowed limit of 4MB."
        super().__init__(self.message)

    def __str__(self):
        return self.message


class ContentTypeNotAllowed(Exception):
    """Exception raised for errors in file processing

    Attributes:
        invalid_type -- file type not allowed
        accepted_types -- accepted file extensions
    """

    def __init__(self, invalid_type, accepted_types):
        self.invalid_type = invalid_type
        self.accepted_types = accepted_types
        self.message = (
            f"Files of type {invalid_type} are not allowed. "
            f"Please upload a file with the following extensions: {accepted_types}"
        )
        super().__init__(self.message)

    def __str__(self):
        return self.message


class FileController(Controller):
    """
    The FileController class inherits new File controller classes and
    provides them with commonly used methods.
    """

    CHUNK_SIZE = 8192
    IMAGE_EXTENSIONS = {"image/jpeg", "image/png", "image/jpg"}

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(Utils.get_config_ini_file_path())
        self.accepted_files = json.loads(self.config.get("FILES", "accepted_files"))
        self.max_file_size = int(self.config.get("FILES", "max_file_size"))

    def compress_image(self, image_data):
        with Image.open(io.BytesIO(image_data)) as image_data_content:
            b = io.BytesIO()
            image_data_content.save(
                b, image_data_content.format, optimize=True, quality=65
            )
        b.seek(0)
        return b

    def process_stream(self, part: BodyPart):
        self.check_if_valid_content_type(part.content_type)

        read_so_far = 0
        data = []
        while chunk := part.stream.read(self.CHUNK_SIZE):
            data.append(chunk)
            read_so_far += len(chunk)
            if read_so_far > self.max_file_size:
                raise FileSizeGreaterThanAllowed()

        if part.content_type in self.IMAGE_EXTENSIONS:
            return self.compress_image(b"".join(data))

        return b"".join(data)

    def on_post(self, req: Request, resp: Response, id: int = None):
        if id:
            self.response(resp, HTTPStatus.METHOD_NOT_ALLOWED)
            return

        session = self.get_session(req, resp)
        if not session:
            return

        make_thumbnail = self.check_if_make_thumbnail(req)
        public_file = self.check_if_public_file(req)
        private_file = self.check_if_private_file(req)
        form = req.get_media()
        for part in form:
            part: BodyPart = part
            try:
                stream_content = self.process_stream(part)
            except Exception as e:
                self.response(resp, HTTPStatus.BAD_REQUEST, error=str(e))
                return

            file_data, thumbnail_data, code = self.process_file(
                part.filename,
                stream_content,
                part.content_type,
                user=session.user,
                make_thumbnail=make_thumbnail,
                public=public_file,
                private=private_file
            )
            data = [file_data]
            if thumbnail_data:
                data.append(thumbnail_data)
            break

        self.response(resp, code, data)

    def on_post_base64(self, req: Request, resp: Response, id: int = None):
        if id:
            self.response(resp, HTTPStatus.METHOD_NOT_ALLOWED)
            return
        
        session = self.get_session(req, resp)
        if not session:
            return

        base64_info, file_name, error_message = self.get_base64_info(req)
        if not base64_info:
            self.response(resp, HTTPStatus.BAD_REQUEST, error=error_message)
            return

        base64_decoded = self.decode_base64_file(base64_info)
        mimetype = self.get_mimetype(base64_decoded)

        try:
            self.check_if_valid_content_type(mimetype)
        except ContentTypeNotAllowed as e:
            self.response(resp, HTTPStatus.BAD_REQUEST, error=str(e))
            return

        make_thumbnail = self.check_if_make_thumbnail(req)
        public_file = self.check_if_public_file(req)
        private_file = self.check_if_private_file(req)
        file, thumbnail, code = self.process_file(
            file_name,
            base64_decoded,
            mimetype,
            user=session.user,
            make_thumbnail=make_thumbnail,
            public=public_file,
            private=private_file
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

    def check_if_public_file(self, req: Request):
        return req.params.get("public") == "True"

    def check_if_private_file(self, req: Request):
        return req.params.get("private") == "True"

    def process_file(
        self,
        filename,
        data,
        content_type,
        user: User,
        encode_to_base64=False,
        make_thumbnail=False,
        public=False,
        private=False
    ):
        file = self.create_file(filename, data, content_type, encode_to_base64=encode_to_base64, user=user, public=public, private=private)

        if not file:
            return {"Filename": filename, "Error": self.PROBLEM_SAVING_TO_DB}, None, 500

        thumbnail = None
        if make_thumbnail and content_type in self.IMAGE_EXTENSIONS:
            thumbnail = self.create_thumbnail(
                data,
                filename,
                content_type,
                encode_to_base64,
                user=user,
                public=public,
                private=private
            )
            thumbnail = Utils.serialize_model(thumbnail) if thumbnail else {"Filename_thumbnail": filename, "error": self.PROBLEM_SAVING_TO_DB}

        return Utils.serialize_model(file), thumbnail, 201

    def create_thumbnail(self, image_data, filename, content_type, encode_to_base64, user: User, public=False, private=False):
        thumbnail_content = self.create_thumbnail_image(image_data)
        filename = filename.split(".")
        thumbnail_name = (
            filename[0]
            + "_thumbnail"
            + ("." + filename[1] if len(filename) > 1 else "")
        )
        return self.create_file(
            thumbnail_name,
            thumbnail_content,
            content_type,
            user=user,
            is_thumbnail=1,
            encode_to_base64=encode_to_base64,
            public=public,
            private=False
        )

    def create_thumbnail_image(self, image_data):
        if not isinstance(image_data, io.BytesIO):
            image_data = io.BytesIO(image_data)

        with Image.open(image_data) as image_data_content:
            image_data_content.thumbnail(size=(640, 640))
            b = io.BytesIO()
            image_data_content.save(b, image_data_content.format)
        b.seek(0)
        return b

    def decode_base64_file(self, base64_info):
        return base64.b64decode(base64_info)

    def encode_to_base64(self, data):
        return base64.b64encode(data)

    def get_mimetype(self, data):
        return filetype.guess(data).mime

    def get_base64_file_length(self, b64string):
        return (len(b64string) * 3) / 4 - b64string.count("=", -1, -5)

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
            return None, None, f"The file {file_name} is larger than 4mb."

        return base64_info, file_name, None

    def format_file_content(self, file_content):
        if isinstance(file_content, str):
            file_content = file_content.encode("utf-8")
        elif not isinstance(file_content, bytes):
            file_content = file_content.read()

        return file_content


class FileAbstract(ABC):
    """
    Abstract class that all FileController subclasses should implement
    """

    @abstractmethod
    def create_file(
        self,
        file_name: str,
        file_content,
        file_type,
        is_thumbnail=0,
        encode_to_base64=True,
    ):
        pass
