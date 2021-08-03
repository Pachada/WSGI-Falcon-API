from controllers import *
import configparser
from core.classes.Authenticator import Authenticator
from falcon import API

class RouteLoader():

    def __init__(self, server, authorization_middleware):
        self.server:API = server
        self.authorization_middleware:Authenticator = authorization_middleware
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.context_from_config = self.config.get('ROUTES', 'context')
        self.context_prefix = '/'+self.context_from_config if self.context_from_config != '' else ''

    def loadExceptionRoutes(self):
        self.authorization_middleware.add_exception_route(self.context_prefix + '/health-check/ping')
        self.authorization_middleware.add_exception_route(self.context_prefix + '/password-recovery/request')
        self.authorization_middleware.add_exception_route(self.context_prefix + '/password-recovery/validate-code')
        self.authorization_middleware.add_exception_route(self.context_prefix + '/sessions/login')
        self.authorization_middleware.add_exception_route(self.context_prefix + '/test')
        self.authorization_middleware.add_exception_route(self.context_prefix + '/users')
        

        # BackOffice
        self.server.add_route(self.context_prefix + "/users", userController)
        self.server.add_route(self.context_prefix + "/users/{id:int}", userController)
        self.server.add_route(self.context_prefix + "/persons", personController)
        self.server.add_route(
            self.context_prefix + "/persons/{id:int}", personController
        )
        self.server.add_route(self.context_prefix + "/roles", roleController)
        self.server.add_route(self.context_prefix + "/roles/{id:int}", roleController)
        self.server.add_route(self.context_prefix + "/devices", deviceController)
        self.server.add_route(
            self.context_prefix + "/devices/{id:int}", deviceController
        )
        self.server.add_route(
            self.context_prefix + "/devices/token", deviceController, suffix="token"
        )

        #BackOffice
        self.server.add_route(self.context_prefix + '/users', userController)
        self.server.add_route(self.context_prefix + '/users/{id:int}', userController)
        self.server.add_route(self.context_prefix + '/persons', personController)
        self.server.add_route(self.context_prefix + '/persons/{id:int}', personController)
        self.server.add_route(self.context_prefix + '/roles', roleController)
        self.server.add_route(self.context_prefix + '/roles/{id:int}', roleController)
        self.server.add_route(self.context_prefix + '/devices', deviceController)
        self.server.add_route(self.context_prefix + '/devices/{id:int}', deviceController)
        self.server.add_route(self.context_prefix + '/devices/token', deviceController, suffix='token')