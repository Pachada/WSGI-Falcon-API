from core.Model import *
from core.Utils import Utils
import os


class File(Base, Model):

    DEFAULT_LOCAL_LOGO = 709
    DEFAULT_VISITOR_LOGO = 878
    
    __tablename__ 	= 'file'

    id = Column(Integer, primary_key=True, autoincrement=True)
    object = Column(String(255), nullable=False)
    size = Column(Integer, nullable=False)
    type = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    hash = Column(String(255), nullable=False)
    is_thumbnail = Column(mysql.TINYINT(1), default=0)
    created = Column(DateTime, default = Utils.time())
    updated = Column(DateTime, default = Utils.time(), onupdate =  Utils.time())
    enable = Column(Boolean, default=True)

    formatters = {
        "created": Utils.date_formatter,
        "updated": Utils.date_formatter
    }
    

    def delete_file_from_s3(self, req, resp):
        print(f"Borrando file: {self.id} del s3")
        from controllers import files3Controller
        files3Controller.on_delete(req, resp, self.id)


    def delete_file_from_local(self, req, resp):
        pass
        #print(f"Borrando file: {self.id} del local")
        #from controllers import filelocalController
        #filelocalController.on_delete(req, resp, self.id)