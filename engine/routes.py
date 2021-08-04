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
        

    def loadRoutes(self):
        self.server.add_route(self.context_prefix + '/test', testController)
        self.server.add_route(self.context_prefix + '/health-check/{action}', healthcheckController) #ping
        self.server.add_route(self.context_prefix + '/sessions/{action}', sessionController) #login, logout
        self.server.add_route(self.context_prefix + '/sessions', sessionController)
        self.server.add_route(self.context_prefix + '/password-recovery/{action}', passwordrecoveryController) #request, validate-code, change-password
        self.server.add_route(self.context_prefix + '/confirm-email/{action}', confirmemailController) #request, validate-code
        self.server.add_route(self.context_prefix + '/status', statusController)
        self.server.add_route(self.context_prefix + '/status/{id:int}', statusController)
        self.server.add_route(self.context_prefix + '/files/local', filelocalController, suffix='local')
        self.server.add_route(self.context_prefix + '/files/local/{id:int}', filelocalController, suffix='local')
        self.server.add_route(self.context_prefix + '/files/local/base64', filelocalController, suffix='base64')
        self.server.add_route(self.context_prefix + '/files/local/image', filelocalController, suffix='image')
        self.server.add_route(self.context_prefix + '/files/local/image/{id:int}', filelocalController, suffix='image')
        self.server.add_route(self.context_prefix + '/files/s3', files3Controller)
        self.server.add_route(self.context_prefix + '/files/s3/{id:int}', files3Controller)
        self.server.add_route(self.context_prefix + '/files/s3/base64', files3Controller, suffix='base64')
        self.server.add_route(self.context_prefix + '/files/s3/base64/{id:int}', files3Controller, suffix='base64')
        self.server.add_route(self.context_prefix + '/notifications', notificationController)
        self.server.add_route(self.context_prefix + '/notifications/{id:int}', notificationController)

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