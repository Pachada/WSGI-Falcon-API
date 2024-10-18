import os
import tempfile

import filetype

from core.classes.aws.S3Handler import S3Handler
from models.File import File, logger


class FileManager:
    """
    The FileManager Class helps you to management files with methods to get information about a file,
    put a file or get a file using S3Handler Class.
    """

    @staticmethod
    def get_file_info(file_path):
        """
        The getFileInfo() method gets information of a file and return it in a dictionary.

        Parameters
        ----------
        file_path : `str`
                A string for file path.

        Returns
        -------
        `dict`
            A dictionary with size, name, hash and type oof file."""

        if os.path.exists(file_path):
            size = os.stat(file_path).st_size
            name = os.path.basename(file_path)
            _type = filetype.guess(file_path).mime
            # hash = hashlib.sha224(name + str(size)).hexdigest()
            return {
                "size": size,
                "name": name,
                # 'hash': hash,
                "type": _type,
            }
        else:
            return None

    @staticmethod
    def put_file(
        bucket_name,
        content,
        key,
        user_id,
        file_type=None,
        file_name=None,
        profile=None,
        region="us-west-2",
        metadata=None,
        is_thumbnail=0,
        url=None,
        is_private=False
    ):
        """
        The putFile() method creates a temporary file and write inside it the content,
        then creates a new handler of S3Handler class to use upload_file() method, finally
        saves a record file with metadata of file and return an instance of saved file.

        Parameters
        ----------
        bucket_name : `str`
                A string of bucket name.
        profile : `str`
                A string of profile name.
        content : `type`
                Content of file.
        key : `str`
                A string of key.
        region : `str`
                A string of region.
        metadata : `dict`
                A dictionary of metadata, empty by default.

        Returns
        -------
        `models.File.File`
            An instance of the saved file.
            """
        if metadata is None:
            metadata = {}
        tmpFile = tempfile.NamedTemporaryFile()
        tmpFile.write(content)
        tmpFile.seek(0)
        metadata_info = FileManager.get_file_info(tmpFile.name)
        handler = S3Handler(bucket_name, region, profile)
        obj = handler.upload_file(tmpFile, key, metadata=metadata)

        record = File(
            object=key,
            size=metadata_info.get("size"),
            type=file_type or metadata_info.get("type"),
            name=file_name or metadata_info.get("name"),
            hash=key,
            is_thumbnail=is_thumbnail,
            user_who_uploaded_id=user_id,
            url=url,
            is_private=is_private
        )

        tmpFile.close()

        return record if record.save() else None

    @staticmethod
    def get_file(bucket_name, file_id, aws_region, profile=None):
        """
        The getfile() method gets a file from database and creates a handler to download it using
        download_file() method.

        Parameters
        ----------
        bucket_name : `str`
                A string of bucket name.
        profile : `str`
                A string of profile name.
        idFile : `int`
                An integer of idFile
        aws_region : `str`
                A string of Amazon web service region.

        Returns
        -------
        `instance`
            An instance of the downloaded file.
            """
        if file := File.get(file_id):
            handler = S3Handler(bucket_name, aws_region, profile=profile)
            try:
                fileobj = handler.download_file(file.object)
                return file, fileobj
            except Exception as e:
                logger.error("[ERROR-GETTING-FILE-FROM-S3]")
                logger.error(e)
                return file, None

        return None, None

    @staticmethod
    def delete_file(bucket_name, public_bucket_name, file: File, aws_region, profile=None):
        bucket = bucket_name
        # If the file has url that means is public and we should look in the public bucket
        if file.url:
            bucket = public_bucket_name

        handler = S3Handler(bucket, aws_region, profile=profile)
        try:
            return handler.delete_file(file.object)
        except Exception as e:
            logger.error(e)
            return
