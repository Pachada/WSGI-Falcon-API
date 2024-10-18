import os
import time
from random import randint

from core.classes.FileUtils import (ROUTE_LOADER, File, FileAbstract,
                                    FileController, HTTPStatus, Request,
                                    Response, User, Utils, logger)
from models.Role import Role


@ROUTE_LOADER('/v1/files/local')
@ROUTE_LOADER('/v1/files/local/{id:int}')
@ROUTE_LOADER('/v1/files/local/base64', suffix="base64")
@ROUTE_LOADER('/v1/files/local/base64/{id:int}', suffix="base64")
class FileLocalController(FileController, FileAbstract):
    def __init__(self):
        super().__init__()
        self.storage_path = self.config.get("FILES", "storage_path")

    def on_get(self, req: Request, resp: Response, id: int = None):
        if not id:
            self.response(resp, HTTPStatus.METHOD_NOT_ALLOWED)
            return

        file = File.get(id)
        if not file:
            self.response(resp, HTTPStatus.NOT_FOUND, error="No  file")
            return

        session = self.get_session(req, resp)
        if not session:
            return
        user: User = session.user
        user_role: Role = user.role
        if file.is_private and user_role != Role.ADMIN and user.id != file.user_who_uploaded_id:
            self.response(resp, HTTPStatus.FORBIDDEN, error="Private file")
            return

        if not os.path.exists(file.object):
            self.response(resp, HTTPStatus.CONFLICT, error="File content not found")
            return

        resp.set_header("content-disposition", f'inline; filename="{file.name}"')
        resp.stream = open(file.object, "rb")
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
            self.response(resp, HTTPStatus.NOT_FOUND, message="No such file or directory")
            return

        session = self.get_session(req, resp)
        if not session:
            return
        user: User = session.user
        user_role: Role = user.role
        if user_role != Role.ADMIN and user.id != file.user_who_uploaded_id:
            self.response(resp, HTTPStatus.FORBIDDEN, error="You can only delete your own files")
            return

        self.__delete_file(file, soft_delete=False)
        self.response(resp, HTTPStatus.OK, Utils.serialize_model(file))

    # -------------------------------- base64 --------------------------------

    def on_get_base64(self, req: Request, resp: Response, id: int = None):
        try:
            if id:
                file = File.get(id)
                if not file:
                    self.response(resp, HTTPStatus.NOT_FOUND, message="No such file or directory")
                    return
            else:
                file = File.get_all()

            self.response(resp, HTTPStatus.OK, self.__get_file_data_as_base64(file))

        except Exception as exc:
            logger.error(exc)
            self.response(resp, HTTPStatus.INTERNAL_SERVER_ERROR, error=str(exc))

    # -------------------------------- Utils --------------------------------

    def __get_file_data_as_base64(self, file, base64=False):
        """Returns the the information of the file

        Parameters
        ----------
        file : list or File
            A list of File objects or a File object
        base64: bool
            if the info of the file is neede in base64

        Returns
        -------
        list
            a list of dictionaries containing the info of the files.
        dict
            a dict with the info of the file
        """

        if isinstance(file, list):
            return [self.__get_file_data_as_base64(item) for item in file]

        elif isinstance(file, File):

            if not os.path.exists(file.object):
                # self.__delete_file(file)
                return {"id": file.id, "message": "No such file or directory"}

            with open(file.object, "rb") as file_object:
                file_content = super().encode_to_base64(file_object.read())
                data = Utils.serialize_model(file)
                # The base64 has 'trash' in it, remove it with a trim [2:-1]
                data["base64"] = str(file_content)[2:-1]

            return data

    def __delete_file(self, file, soft_delete=True):
        """Soft deletes the file and removes the file content from the server.

        Parameters
        ----------
        file : list or File
            A list of File objects to delete or a File object

        Returns
        -------
        None
        """
        if isinstance(file, list):
            for item in file:
                self.__delete_file(item)
            return

        elif isinstance(file, File):
            if soft_delete:
                file.soft_delete()
            else:
                file.delete()
            if os.path.exists(file.object):
                os.remove(file.object)

    def create_file(
        self,
        file_name: str,
        file_content,
        file_type,
        user: User,
        is_thumbnail=0,
        encode_to_base64=True,
        public=False,
        private=False
    ):
        random_number = randint(0, 100000)
        filename = (
            str(random_number) + file_name[:-4] + str(time.time()) + file_name[-4:]
        )
        file_path = os.path.join(self.storage_path, filename)

        # Write to a temporary file to prevent incomplete files
        # from being used.
        temp_file_path = file_path + "~"

        file_content = super().format_file_content(file_content)

        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(file_content)

        # Now that we know the file has been fully saved to disk
        # move it into place.
        os.rename(temp_file_path, file_path)

        file = File(
            size=os.stat(file_path).st_size,
            type=file_type,
            name=file_name,
            is_thumbnail=is_thumbnail,
            user_who_uploaded_id=user.id,
            is_private=private
        )

        hash_string = (
            str(file.size)
            + str(file.name)
            + str(file.type)
            + str(file.created)
            + str(time.time())
            + str(filename)
        )
        file.hash = Utils.get_hashed_string(hash_string)

        file_path_hashed = os.path.join(self.storage_path, file.hash)
        os.rename(file_path, file_path_hashed)
        file.object = file_path_hashed

        if not file.save():
            self.__delete_file(file, False)
            return None

        if encode_to_base64:
            # Now that we have the info of the file, encode it in base64
            with open(file_path_hashed, "wb") as file_path_to_encode:
                file_content = super().encode_to_base64(file_content)
                file_path_to_encode.write(file_content)

        return file
