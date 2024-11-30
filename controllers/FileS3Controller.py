import time
from io import BufferedReader

from core.classes.FileManager import FileManager
from core.classes.FileUtils import (ROUTE_LOADER, File, FileAbstract,
                                    FileController, HTTPStatus, Request,
                                    Response, Utils)
from models.User import Role, User


@ROUTE_LOADER('/v1/files/s3')
@ROUTE_LOADER('/v1/files/s3/{id:int}')
@ROUTE_LOADER('/v1/files/s3/base64', suffix="base64")
@ROUTE_LOADER('/v1/files/s3/base64/{id:int}', suffix="base64")
class FileS3Controller(FileController, FileAbstract):
    def __init__(self):
        super().__init__()
        #  AWS S3 info
        self.bucket = self.config.get("S3", "bucket_name")
        self.public_bucket = self.config.get("S3", "public_bucket_name")
        self.region = self.config.get("S3", "region")
        self.profile = self.config.get("S3", "profile_name")

    def on_get(self, req: Request, resp: Response, id: int = None):
        if not id:
            self.response(resp, HTTPStatus.METHOD_NOT_ALLOWED)
            return

        file, file_object = FileManager.get_file(self.bucket, id, self.region)

        if not file:
            self.response(resp, HTTPStatus.NOT_FOUND, error="No file with that id")
            return

        if not file_object:
            self.response(resp, HTTPStatus.INTERNAL_SERVER_ERROR, error="Error geting file from s3")
            return
        
        file: File = file
        session = self.get_session(req, resp)
        if not session:
            return
        user: User = session.user
        user_role: Role = user.role
        if file.is_private and user_role != Role.ADMIN and user.id != file.user_who_uploaded_id:
            self.response(resp, HTTPStatus.FORBIDDEN, error="Private file")
            return

        resp.set_header("content-disposition", f'inline; filename="{file.name}"')
        resp.stream = BufferedReader(file_object)
        resp.content_length = file.size
        resp.content_type = file.type

    def on_post(self, req: Request, resp: Response, id: int = None):
        return super().on_post(req, resp, id)
    
    def on_post_base64(self,  req: Request, resp: Response, id: int = None):
        return super().on_post_base64(req, resp, id)

    def on_delete(self, req: Request, resp: Response, id: int = None):
        if not id:
            self.response(resp, HTTPStatus.METHOD_NOT_ALLOWED)
            return

        file = File.get(id)
        if not file:
            self.response(resp, HTTPStatus.NOT_FOUND, error=self.ID_NOT_FOUND)
            return

        session = self.get_session(req, resp)
        if not session:
            return
        user: User = session.user
        user_role: Role = user.role
        if user_role != Role.ADMIN and user.id != file.user_who_uploaded_id:
            self.response(resp, HTTPStatus.FORBIDDEN, error="You can only delete your own files")
            return

        if not FileManager.delete_file(self.bucket, self.public_bucket, file, self.region):
            self.response(resp, HTTPStatus.INTERNAL_SERVER_ERROR, error="Error deleting file from S3")
            return

        if not file.delete():
            self.response(resp, HTTPStatus.INTERNAL_SERVER_ERROR, error="File deleted from S3, but failed to deleted from database")
            return

        self.response(resp, HTTPStatus.OK, Utils.serialize_model(file))

    # -------------------------------- base64 --------------------------------

    def on_get_base64(self, req: Request, resp: Response, id: int = None):
        if not id:
            self.response(resp, HTTPStatus.METHOD_NOT_ALLOWED)
            return

        file, file_object = FileManager.get_file(self.bucket, id, self.region)

        if not file:
            self.response(resp, HTTPStatus.NOT_FOUND, error="No file with that id")
            return

        file_content = file_object.read()
        file_object.close()
        file_content_b64 = super().encode_to_base64(file_content)
        data = Utils.serialize_model(file)
        data["base64"] = str(file_content_b64)[2:-1]

        self.response(resp, HTTPStatus.OK, data)

    # -------------------------------- Utils --------------------------------

    def create_file(
        self,
        file_name,
        file_content,
        file_type,
        user: User,
        is_thumbnail=0,
        encode_to_base64=False,
        public=False,
        private=False,
        metadata=None
    ):
        file_content = super().format_file_content(file_content)

        hash_string = file_name + file_type + str(time.time()) + str(file_content)[:25]
        file_hash = Utils.get_hashed_string(hash_string)

        if encode_to_base64:
            file_content = super().encode_to_base64(file_content)

        bucket = self.bucket
        url = None
        # For public files, append file extension to key and setup public URL
        if public:
            bucket = self.public_bucket
            file_type_new = file_type.split("/")[1]
            file_hash = f"{file_hash}.{file_type_new}"
            url = f"https://{bucket}.s3.amazonaws.com/{file_hash}"  # https://bucket_name.s3.amazonaws.com/6d9860c300a8744cbbf3f5.png
            metadata = {'Content-Type': file_type}
        
        return FileManager.put_file(
            bucket,
            file_content,
            file_hash,
            user_id=user.id,
            file_type=file_type,
            file_name=file_name,
            region=self.region,
            is_thumbnail=is_thumbnail,
            url=url,
            is_private=private,
            metadata=metadata
        )
