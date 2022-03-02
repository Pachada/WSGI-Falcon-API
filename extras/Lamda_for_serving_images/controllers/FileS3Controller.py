from core.classes.FileUtils import (
    FileController,
    Utils,
    File,
    Request,
    Response,
)
from io import BufferedReader
from core.classes.FileManager import FileManager


class FileS3Controller(FileController):
    def __init__(self):
        super().__init__()
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

        if not file_object:
            self.response(resp, 500, error="Error geting file from s3")
            return

        resp.set_header("content-disposition", f'inline; filename="{file.name}"')
        resp.stream = BufferedReader(file_object)
        resp.content_length = file.size
        resp.content_type = file.type

    # -------------------------------- base64 --------------------------------

    def on_get_base64(self, req: Request, resp: Response, id: int = None):
        if not id:
            self.response(resp, 405)
            return

        file, file_object = FileManager.get_file(self.bucket, id, self.region)

        if not file:
            self.response(resp, 404, error="No file with that id")
            return

        file_content = file_object.read()
        file_object.close()
        file_content_b64 = super().encode_to_base64(file_content)
        data = Utils.serialize_model(file)
        data["base64"] = str(file_content_b64)[2:-1]

        self.response(resp, 200, data)


