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


class FileController(Controller):

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        # list of accepted files types
        self.accepted_files = json.loads(self.config.get("FILES", "accepted_files"))
        # Maximum file size accepted
        self.max_file_size = int(self.config.get("FILES", "max_file_size"))

    def on_post(self, req: Request, resp: Response, id: int = None):
        if id:
            self.response(resp, 405)
            return

        make_thumbnail = self.check_if_make_thumbnail(req)
        data = []
        form = req.get_media()
        for part in form:
            part: BodyPart = part
            file, thumbnail, code = self.procces_file(
                part.filename,
                part.stream.read(),
                part.content_type,
                make_thumbnail=make_thumbnail,
            )
            data.append(file)
            if thumbnail:
                data.append(thumbnail)
        # TODO check a way to send other HTTP code
        # Maybe only accept one file at a time?
        self.response(resp, code, data)

    def on_post_base64(self, req: Request, resp: Response, id: int = None):
        if id:
            self.response(resp, 405)
            return

        base64_info, file_name, error_message = self.get_base64_info(req)
        if not base64_info:
            self.response(resp, 400, errror=error_message)
            return

        base64_decoded = self.decode_base64_file(base64_info)
        mimetype = self.get_mimetype(base64_decoded)
        make_thumbnail = self.check_if_make_thumbnail(req)
        file, thumbnail, code = self.procces_file(
            file_name, base64_decoded, mimetype, make_thumbnail=make_thumbnail
        )
        data = file
        if thumbnail:
            data = [file, thumbnail]

        self.response(resp, code, data)

    def delete_file_objects(self, req, resp, file_objects: list):
        if file_objects:
            for item in file_objects:
                self.on_delete(req, resp, item.id)

    def check_if_valid_content_type(self, content_type):
        return content_type in self.accepted_files

    def check_if_valid_file_size(self, data):
        return sys.getsizeof(data) < self.max_file_size

    def check_if_make_thumbnail(self, req: Request):
        query_string = req.params
        return query_string.get("thumbnail") == "True"

    def procces_file(
        self, filename, data, content_type, encode_to_base64=False, make_thumbnail=False
    ):

        if not self.check_if_valid_content_type(content_type):
            return (
                {
                    "Filename": filename,
                    "Error": (
                        f"files of type {content_type} are not accepted, "
                        f"please submit a valid file format: {self.accepted_files}"
                    ),
                },
                None,
                400,
            )

        if not self.check_if_valid_file_size(data):
            return (
                {"Filename": filename, "Error": f"{filename} content is to large."},
                None,
                400,
            )

        file = self.create_file(
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
        return self.create_file(
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

    def get_base64_info(self, req: Request):
        try:
            data: dict = json.loads(req.stream.read())
        except Exception as exc:
            return None, None, str(exc)

        base64_info: str = data.get("base64")
        file_name = data.get("file_name")
        if not file_name or not base64_info:
            return None, None, "'file_name' and 'base64' needed"

        return base64_info, file_name, None

    def format_file_content(self, file_content):
        if isinstance(file_content, str):
            file_content = file_content.encode("utf-8")

        elif not isinstance(file_content, bytes):
            file_content = file_content.read()

        return file_content
