from controllers import *
import configparser
from core.classes.Authenticator import Authenticator
from falcon import API
from core.Utils import Utils


class RouteLoader:
    def __init__(self, server, authorization_middleware):
        self.server: API = server
        self.authorization_middleware: Authenticator = authorization_middleware
        self.config = configparser.ConfigParser()
        self.config.read(Utils.get_config_ini_file_path())
        self.context_from_config = self.config.get('ROUTES', 'context')
        self.context_prefix = (
            f'/{self.context_from_config}'
            if self.context_from_config != ''
            else ''
        )

    def loadExceptionRoutes(self):
        self.authorization_middleware.add_exception_route(
            f'{self.context_prefix}/health-check/ping'
        )

        self.load_mails_routes()
        self.load_icon_routes()
        

    def loadRoutes(self):
        self.server.add_route(self.context_prefix + '/health-check/{action}', healthcheckController) #ping
        self.server.add_route(f'{self.context_prefix}/files/s3', files3Controller)
        self.server.add_route(self.context_prefix + '/files/s3/{id:int}', files3Controller)
        self.server.add_route(
            f'{self.context_prefix}/files/s3/base64',
            files3Controller,
            suffix='base64',
        )

        self.server.add_route(self.context_prefix + '/files/s3/base64/{id:int}', files3Controller, suffix='base64')

    def load_mails_routes(self):
        # Imagenes de los correos

        # Ganador
        # Logo Duelazo
        self.authorization_middleware.add_exception_route(
            f'{self.context_prefix}/files/local/image/354'
        )

        self.authorization_middleware.add_exception_route(
            f'{self.context_prefix}/files/s3/1014'
        )

        # background
        self.authorization_middleware.add_exception_route(
            f'{self.context_prefix}/files/local/image/355'
        )

        self.authorization_middleware.add_exception_route(
            f'{self.context_prefix}/files/s3/1015'
        )

        # medalla2x
        self.authorization_middleware.add_exception_route(
            f'{self.context_prefix}/files/local/image/356'
        )

        self.authorization_middleware.add_exception_route(
            f'{self.context_prefix}/files/s3/1016'
        )


        #Recuperar contraseña
        #body
        self.authorization_middleware.add_exception_route(
            f'{self.context_prefix}/files/local/image/357'
        )

        self.authorization_middleware.add_exception_route(
            f'{self.context_prefix}/files/s3/1017'
        )

        #bottom - card
        self.authorization_middleware.add_exception_route(
            f'{self.context_prefix}/files/local/image/358'
        )

        self.authorization_middleware.add_exception_route(
            f'{self.context_prefix}/files/s3/1018'
        )

        # top-card
        self.authorization_middleware.add_exception_route(
            f'{self.context_prefix}/files/local/image/359'
        )

        self.authorization_middleware.add_exception_route(
            f'{self.context_prefix}/files/s3/1019'
        )


        #Quiniela finalizada 
        # Phone Screen
        self.authorization_middleware.add_exception_route(
            f'{self.context_prefix}/files/local/image/360'
        )

        self.authorization_middleware.add_exception_route(
            f'{self.context_prefix}/files/s3/1020'
        )

        self.authorization_middleware.add_exception_route(
            f'{self.context_prefix}/files/s3/1058'
        )

        #Apple logo
        self.authorization_middleware.add_exception_route(
            f'{self.context_prefix}/files/local/image/479'
        )

        self.authorization_middleware.add_exception_route(
            f'{self.context_prefix}/files/s3/1021'
        )
    

    def load_icon_routes(self):
        # Imagenes de las push

        # small_icon
        self.authorization_middleware.add_exception_route(
            f'{self.context_prefix}/files/s3/991'
        )

        # medium icon
        self.authorization_middleware.add_exception_route(
            f'{self.context_prefix}/files/s3/992'
        )