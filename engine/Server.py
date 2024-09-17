import falcon

from core.classes.middleware.Authenticator import Authenticator
from core.classes.middleware.SQLAlchemySessionManager import \
    SQLAlchemySessionManager
from engine.RouteLoader import RouteLoader

authorization_middleware = Authenticator()
sqlalchemy_session_manager = SQLAlchemySessionManager()

# Create server
server = falcon.App(cors_enable=True, middleware=[authorization_middleware, sqlalchemy_session_manager])

# Load routes
route_loader = RouteLoader(server)
# initialize all controllers
from controllers import *
