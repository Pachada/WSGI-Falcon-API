import falcon
from engine.routes import RouteLoader
from core.classes.Authenticator import Authenticator
from core.classes.CORS_Handler import CORS_Handler
from core.classes.SQLAlchemySessionManager import SQLAlchemySessionManager

authorization_middleware = Authenticator()
CORS_middleware = CORS_Handler()
sqlalchemy_session_manager = SQLAlchemySessionManager()

# Create server
server = falcon.App(
    middleware=[CORS_middleware, authorization_middleware, sqlalchemy_session_manager]
)
# server = falcon.App()

# Load routes
routeLoader = RouteLoader(server, authorization_middleware)
routeLoader.loadRoutes()
routeLoader.loadExceptionRoutes()
