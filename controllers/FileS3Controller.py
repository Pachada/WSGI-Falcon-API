from falcon.request import Request
from falcon.response import Response
from core.Controller import Controller, time, json
from core.Utils import Utils
from models.File import File
import configparser
from PIL import Image
import io
import sys
import base64
from falcon.media.multipart import BodyPart, MultipartParseError, MultipartParseOptions
import magic
from core.classes.FileManager import FileManager


class FileS3Controller(Controller):
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        # list of accepted files types
        self.accepted_files = json.loads(self.config.get("FILES", "accepted_files"))
        # Maximum file size accepted
        self.max_file_size = int(self.config.get("FILES", "max_file_size"))
        #  AWS S3 info
        self.bucket = self.config.get("S3", "bucket_name")
        self.region = self.config.get("S3", "region")
        self.profile = self.config.get("S3", "profile_name")

    def on_get(self, req: Request, resp: Response, id: int = None):
        if not id:
            self.response(resp, 405)
            return

        file, file_object = FileManager.get_file(self.bucket, id, self.region)

        if not file:
            self.response(resp, 404, error="No file with that id")
            return

        file_content = file_object.read()
        data = Utils.serialize_model(file)
        data["base64"] = str(file_content)[2:-1]
        file_object.close()

        self.response(resp, 200, data)

    def on_delete(self, req: Request, resp: Response, id: int = None):
        if not id:
            self.response(resp, 405)
            return

        file, deleted = FileManager.delete_file(self.bucket, id, self.region)
        if not file:
            self.response(resp, 404, error=self.ID_NOT_FOUND)
            return

        if not deleted:
            self.response(resp, 500, error="Error deleting file from S3")
            return

        if not file.soft_delete():
            self.response(
                resp,
                500,
                error="File deleted from S3, but failed to deleted from database",
            )
            return

        self.response(resp, 200, Utils.serialize_model(file))

    def on_post_base64(self, req: Request, resp: Response, id: int = None):
        print("Saving file in s3 server")
        if id:
            self.response(resp, 405)
            return

        data: dict = json.loads(req.stream.read())
        base64_info: str = data.get("base64")
        file_name = data.get("file_name")
        if not file_name or not base64_info:
            self.response(resp, 400, error="'file_name' and 'base64' needed")
            return

        mimetype = magic.from_buffer(base64.b64decode(base64_info), mime=True)

        if mimetype not in self.accepted_files:
            error_message = f"files of type {mimetype} are not accepted, please submit a valid file format: {self.accepted_files}"
            self.response(resp, 400, error=error_message)
            return

        file = self.__create_file_s3(
            file_name, base64_info, mimetype, encode_to_base64=False
        )

        if not file:
            self.response(resp, 500, error="Problem puting image in S3")
            return

        self.response(resp, 201, Utils.serialize_model(file))

    def on_post(self, req: Request, resp: Response, id: int = None):
        print("Saving file in s3 server")
        try:
            if id:
                self.response(resp, 405)
                return

            query_string = req.params
            make_thumbnail = False
            if query_string.get("thumbnail") == "True":
                make_thumbnail = True
            data = []
            file_objects = []
            form = req.get_media()
            for part in form:
                part: BodyPart = part
                if part.content_type not in self.accepted_files:
                    if file_objects:
                        for item in file_objects:
                            self.on_delete(req, resp, item.id)
                    error_message = f"files of type {part.content_type} are not accepted, please submit a valid file format: {self.accepted_files}"
                    self.response(resp, 400, error=error_message)
                    return

                part_data = part.stream.read()
                if sys.getsizeof(part_data) > self.max_file_size:
                    self.response(resp, 413, message=f"{part.name} content is to large")
                    for item in file_objects:
                        self.on_delete(req, resp, item.id)
                    return

                file = self.__create_file_s3(
                    part.filename, part_data, part.content_type
                )
                if not file:
                    data.append(
                        {"file_name": part.name, "error": "Problem saving image in S3"}
                    )
                    continue

                data.append(Utils.serialize_model(file))
                file_objects.append(file)

                if make_thumbnail and (
                    "jpeg" in part.content_type
                    or "png" in part.content_type
                    or "jpg" in part.content_type
                ):
                    thumbnail_content = self.__create_thumbnail(part_data)
                    thumbnail_name = (
                        part.filename[:-4] + "_thumbnail" + part.filename[-4:]
                    )
                    thumbnail = self.__create_file_s3(
                        thumbnail_name,
                        thumbnail_content,
                        part.content_type,
                        is_thumbnail=True,
                    )
                    if not file:
                        data.append(
                            {
                                "thumbnail_of_file_name": part.name,
                                "error": "Problem saving image in S3",
                            }
                        )
                        continue

                    data.append(Utils.serialize_model(thumbnail))
                    file_objects.append(thumbnail)

            self.response(resp, 201, data)

        except Exception as exc:
            print(exc)
            self.response(resp, 400, error=str(exc))

    def __create_file_s3(
        self,
        file_name,
        file_content,
        file_type,
        is_thumbnail=False,
        encode_to_base64=True,
    ):
        if isinstance(file_content, str):
            file_content = file_content.encode("utf-8")

        elif not isinstance(file_content, bytes):
            file_content = file_content.read()

        hash_string = file_name + file_type + str(time.time()) + str(file_content)[:25]
        file_hash = Utils.get_hashed_string(hash_string)

        if encode_to_base64:
            # Now that we have the info of the file, encode it in base64
            file_content = base64.b64encode(file_content)

        file = FileManager.put_file(
            self.bucket,
            file_content,
            file_hash,
            file_type=file_type,
            file_name=file_name,
            region=self.region,
            is_thumbnail=is_thumbnail,
        )
        if file:
            return file

        return None

    def __create_thumbnail(self, image_data):
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
