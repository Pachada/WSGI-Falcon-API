from core.Controller import Controller, datetime, time
from core.Utils import Utils
from models.File import File
from PIL import Image
import io
import os
import hashlib
import base64
import magic
from random import randint
from falcon.media.multipart import BodyPart

class FileController(Controller):

    def __init__(self):
        self.storage_path = './files'

    def on_get_local(self, req, resp, id=None):
        if not id:
            self.response(resp, 405, error = "Specify an id")
            return

        file = File.get(id)
        if not file:
            self.response(resp,404,self.ID_NOT_FOUND)
            return

        file_content = open(file.object, "rb").read()
        data = Utils.serialize_model(file)
        data["base64"] = str(file_content)
        self.response(resp, 200, data)          
    
    def on_post_local(self, req, resp, id=None):
        print("Saving file in local server")
        try:
            if id:
                self.response(resp, 405)
                return

            form = req.get_media()
            data = []
            for part in form:
                part:BodyPart = part
                """if part.name != "file":
                    self.response(resp, 400, error = "Key name should be 'file'") 
                    return"""

                file_content = part.data
                filename = part.filename
                file = self.create_file_local(filename, file_content)
                
                data.append(Utils.serialize_model(file))
                if 'jpeg' in file.type or 'png' in file.type:
                    thumbnail_content = self.create_thumbnail(file_content)
                    thumbnail_name = filename[:-4] + '_thumbnail' + filename[-4:]
                    thumbnail = self.create_file_local(thumbnail_name, thumbnail_content, is_thumbnail=True)
                    data.append(Utils.serialize_model(thumbnail))

            self.response(resp, 201, data)
        except Exception as exc:
            print(exc)
            self.response(resp,400,error = str(exc))

    def create_file_local(self, file_name:str, file_content, is_thumbnail=False):
        random_number = randint(0, 100000)
        filename = str(random_number) + file_name[:-4] + str(time.time()) + file_name[-4:] 
        file_path = os.path.join(self.storage_path, filename)

        # Write to a temporary file to prevent incomplete files
        # from being used.
        temp_file_path = file_path + '~'

        if not isinstance(file_content, bytes):
            file_content = file_content.read()

        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(file_content)
        
        # Now that we know the file has been fully saved to disk
        # move it into place.
        os.rename(temp_file_path, file_path)

        thumbnail = 1 if is_thumbnail else 0
        
        file = File(
            size = os.stat(file_path).st_size, 
            type = magic.from_file(file_path, mime=True),
            name = file_name,
            is_thumbnail = thumbnail
        )

        hash_string = str(file.size) + str(file.name) + str(file.type) + str(file.created) + str(time.time()) + str(filename)
        file.hash = hashlib.sha256(hash_string.encode('utf-8')).hexdigest()

        file_path_hashed = os.path.join(self.storage_path, file.hash)
        os.rename(file_path, file_path_hashed)
        file.object = file_path_hashed

        file.save()

        # Now that we have the info of the file, encode it in base64 
        with open(file_path_hashed, 'wb') as file_path_to_encode:
            file_content = base64.b64encode(file_content)
            file_path_to_encode.write(file_content)
            
        return file

    def create_thumbnail(self, image):
        image = Image.open(io.BytesIO(image))
        image.thumbnail(size=(640,640))
        b = io.BytesIO()
        if image.format == 'PNG':
            image.save(b, "PNG")
        else:
            image.save(b, "JPEG")
        b.seek(0)
        return b

