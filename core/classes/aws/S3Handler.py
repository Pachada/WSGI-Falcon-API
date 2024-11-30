import tempfile
import boto3
from core.Utils import logger


class S3Handler(object):
    """
    The S3Handler Class provides method to handle Amazon web service,
    has methods to upload an download files and set parameters for Amazon S3.
    """

    def __init__(self, bucket_name, region, profile=None):
        """
        The __init__() method sets the bucket name, session by boto3.Session() method giving the profile name,
        s3 using session.resource() method by region name and bucket by se3.Bucket() method with bucket name.

        Parameters
        ----------
        bucket_name : `str`
                A string for bucket name.
        profile : `str`
                A stringr for profile name.
        region : `str`
                A stringr for region name.
        """
        self.bucket_name = bucket_name
        if profile:
            self.session = boto3.Session(profile_name=profile)
        else:
            self.session = boto3.Session()
        self.s3 = self.session.resource("s3", region_name=region)
        self.bucket = self.s3.Bucket(bucket_name)

    def upload_file(self, fileObj, path, metadata={}, public="private"):
        """
        The upload_file() method uploads a new file if a bucket exists using bucket.put_object() method.

        Parameters
        ----------
        fileObj : `instance`
                A instance of fileObj.
        path : `str`
                A string of path.
        metadata : `dict`
                A dictionary of metadata.
        public : `str`
                A string for public, set as private by default.

        Returns
        -------
        `instance`
                A instance of bucket.put_object() method.
        """
        if self.bucket:
            if "Content-Type" in metadata:
                return self.bucket.put_object(
                    Key=path,
                    Body=fileObj,
                    ACL=public,
                    Metadata=metadata,
                    ContentType=metadata["Content-Type"]
                )
            return self.bucket.put_object(
                Key=path,
                Body=fileObj,
                ACL=public,
                Metadata=metadata
            )
        return None

    def download_file(self, path):
        """
        The download_file() method downloads a file in a temporary file if a bucket exists
        using bucket.download_fileobj() method.

        Parameters
        ----------
        path : `str`
                A string of path.

        Returns
        -------
        `instance`
                A instance of a file.
        """
        if self.bucket:
            tmpFile = tempfile.NamedTemporaryFile()
            self.bucket.download_fileobj(path, tmpFile)
            tmpFile.seek(0)
            return tmpFile
        logger.error("No Bucket")
        return None

    def delete_file(self, key):
        """
        The delete_file() method deletes a file if a bucket exists
        using bucket.delete_key() method.

        Parameters
        ----------
        path : `key`
                A string of the key to delete.

        Returns
        -------
        `bool`
                True if file was deleted successfully, False otherwise
        """
        if self.bucket:
            deleted = self.bucket.delete_objects(Delete={"Objects": [{"Key": key}]})
            if len(deleted.get("Deleted")) == 1:
                return True
        return False