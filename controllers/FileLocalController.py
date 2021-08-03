from falcon.request import Request
from falcon.response import Response
from core.Controller import Controller, datetime, time, json
from core.Utils import Utils
from models.File import File
import configparser
from PIL import Image
import io
import os
import sys
import base64
from random import randint
from falcon.media.multipart import BodyPart, MultipartParseError, MultipartParseOptions
import magic


class FileLocalController(Controller):

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        # list of accepted files types
        self.accepted_files = json.loads(self.config.get('FILES', 'accepted_files'))
        # Storage path for saving files localy
        self.storage_path = self.config.get('FILES', 'storage_path')
        # Maximum file size accepted
        self.max_file_size = int(self.config.get('FILES', 'max_file_size'))
    
    def on_get_image(self, req:Request, resp:Response, id:int=None):
        if id:
            file = File.get(id)
            if not file:
                self.response(resp, 404, message =  "No  file")
                return

        resp.stream = open(file.object, "rb")
        resp.content_length = file.size
        resp.content_type = file.type

    def on_post_image(self, req:Request, resp:Response, id:int=None):
        if id:
            self.response(resp, 405)
            return

        return self.__post_local_handler(req, resp, False)

    def on_post_base64(self, req:Request, resp:Response, id:int=None):
        if id:
            self.response(resp, 405)
            return
        
        data:dict = json.loads(req.stream.read())
        base64_info = data.get('base64')
        file_name = data.get('file_name')
        if not file_name or not base64_info:
            self.response(resp, 400, error = "Se nececitan el 'file_name' y el 'base64'")
            return
        
        mimetype = magic.from_buffer(base64.b64decode(base64_info), mime=True)

        if mimetype not in self.accepted_files:
            error_message = f"files of type {mimetype} are not accepted, please submit a valid file format: {self.accepted_files}"
            self.response(resp, 400, error = error_message, error_code = "0004")
            return
        
        file = self.create_file_local(file_name, base64_info, mimetype, encode_to_base64=False)

        self.response(resp, 201, Utils.serialize_model(file))
        

    def on_delete_local(self, req:Request, resp:Response, id:int=None):
        if not id:
            self.response(resp, 405)
            return

        file = File.get(id)
        if not file:
            self.response(resp, 404, message =  "No such file or directory", error_code = "0005")
            return
            
        self.__delete_file(file)
        self.response(resp, 200, Utils.serialize_model(file))
    
    def __delete_file(self, file):
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
            file.soft_delete()
            if os.path.exists(file.object):
                os.remove(file.object)
            
    def on_get_local(self, req:Request, resp:Response, id:int=None):
        try:
            if id:
                file = File.get(id)
                if not file:
                    self.response(resp, 404, message =  "No such file or directory", error_code = "0005")
                    return
            else:
                file = File.getAll()

            self.response(resp, 200, self.__get_file_data(file))
        
        except Exception as exc:
            print(exc)
            self.response(resp, 500, error = str(exc))
        
            
    def __get_file_data(self, file):
        """Returns the the information of the file

        Parameters
        ----------
        file : list or File
            A list of File objects or a File object

        Returns
        -------
        list
            a list of dictionaries containing the info of the files.
        dict
            a dict with the info of the file
        """

        if isinstance(file, list):
            lst = []
            for item in file:
                lst.append(self.__get_file_data(item))
            return lst
        
        elif isinstance(file, File):
        
            if not os.path.exists(file.object):
                self.__delete_file(file)
                return {"id": file.id, "message": "No such file or directory", "code": "0005" }

            with open (file.object, "rb") as file_object:
                file_content = file_object.read()
                data = Utils.serialize_model(file)
                data["base64"] = str(file_content)[2:-1]
            return data

            
    def on_post_local(self, req:Request, resp:Response, id:int=None):
        print("Saving file in local server")
        if id:
            self.response(resp, 405)
            return
        
        return self.__post_local_handler(req, resp, True)

    def create_file_local(self, file_name:str, file_content, file_type, is_thumbnail_flag=0, encode_to_base64=True):
        random_number = randint(0, 100000)
        filename = str(random_number) + file_name[:-4] + str(time.time()) + file_name[-4:] 
        file_path = os.path.join(self.storage_path, filename)

        # Write to a temporary file to prevent incomplete files
        # from being used.
        temp_file_path = file_path + '~'

        if isinstance(file_content, str):
            file_content = file_content.encode('utf-8')

        elif not isinstance(file_content, bytes):
            file_content = file_content.read()
        

        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(file_content)
        
        # Now that we know the file has been fully saved to disk
        # move it into place.
        os.rename(temp_file_path, file_path)
        
        file = File(
            size = os.stat(file_path).st_size, 
            type = file_type,
            name = file_name,
            is_thumbnail = is_thumbnail_flag
        )

        hash_string = str(file.size) + str(file.name) + str(file.type) + str(file.created) + str(time.time()) + str(filename)
        file.hash = Utils.get_hashed_string(hash_string)

        file_path_hashed = os.path.join(self.storage_path, file.hash)
        os.rename(file_path, file_path_hashed)
        file.object = file_path_hashed

        file.save()

        if encode_to_base64:
            # Now that we have the info of the file, encode it in base64 
            with open(file_path_hashed, 'wb') as file_path_to_encode:
                file_content = base64.b64encode(file_content)
                file_path_to_encode.write(file_content)
            
        return file
    
    def create_thumbnail(self, image_data):
        with Image.open(io.BytesIO(image_data)) as image_data_content:
            image_data_content.thumbnail(size=(640,640))
            b = io.BytesIO()
            if image_data_content.format == 'PNG':
                image_data_content.save(b, "PNG")
            elif image_data_content.format == 'JPG':
                image_data_content.save(b, "JPG")
            else:
                image_data_content.save(b, "JPEG")
        b.seek(0)
        return b
    
    def __post_local_handler(self, req:Request, resp:Response, encode_to_base64):
        query_string = req.params
        make_thumbnail = False
        if query_string.get('thumbnail') == 'True': 
            make_thumbnail = True
            
        data = []
        file_objects =  []
        form = req.get_media()
        for part in form:
            part:BodyPart = part
            if part.content_type not in self.accepted_files:
                if file_objects:
                    self.__delete_file(file_objects)
                error_message = f"files of type {part.content_type} are not accepted, please submit a valid file format: {self.accepted_files}"
                self.response(resp, 400, error = error_message)
                return
            
            part_data = part.stream.read()
            if sys.getsizeof(part_data) > self.max_file_size:
                self.response(resp, 413, message=f"{part.name} content is to large")
                if file_objects:
                    self.__delete_file(file_objects)
                return

            file = self.create_file_local(part.filename, part_data, part.content_type, encode_to_base64=encode_to_base64)
            data.append(Utils.serialize_model(file))
            file_objects.append(file)

            if make_thumbnail and ('jpeg' in part.content_type or 'png' in part.content_type or 'jpg' in part.content_type):
                    thumbnail_content = self.create_thumbnail(part_data)
                    thumbnail_name = part.filename[:-4] + '_thumbnail' + part.filename[-4:]
                    thumbnail = self.create_file_local(thumbnail_name, thumbnail_content, part.content_type, is_thumbnail_flag=1)
                    data.append(Utils.serialize_model(thumbnail))
                    file_objects.append(thumbnail)
        
        self.response(resp, 201, data)
