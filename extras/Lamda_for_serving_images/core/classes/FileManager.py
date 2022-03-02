from core.classes.aws.S3Handler import S3Handler
from models.File import File



class FileManager:
    """
    The FileManager Class helps you to management files with methods to get information about a file,
    put a file or get a file using S3Handler Class.
    """

    @staticmethod
    def get_file(bucket_name, file_id, aws_region, profile=None):
        """
                The getfile() method gets a file from database and creates a handler to download it using
                download_file() method.
        ​
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
        ​
                Returns
                -------
                `instance`
                    An instance of the downloaded file."""
        file = File.get(file_id)
        if file:
            handler = S3Handler(bucket_name, aws_region, profile=profile)
            try:
                fileobj = handler.download_file(file.object)
                return file, fileobj
            except Exception as e:
                print("[ERROR-GETTING-FILE-FROM-S3]")
                print(e)
                return file, None

        return None, None

    @staticmethod
    def delete_file(bucket_name, file_id, aws_region, profile=None):
        file = File.get(file_id)
        if not file:
            return None, None

        handler = S3Handler(bucket_name, aws_region, profile=profile)
        try:
            return file, handler.delete_file(file.object)
        except Exception as e:
            print(e)
            return None, None
