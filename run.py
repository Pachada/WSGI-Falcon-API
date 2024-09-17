from gevent.pywsgi import WSGIServer
from engine.Server import server
from core.Utils import logger



def _force_https(app):
    def wrapper(environ, start_response):
        # environ['wsgi.url_scheme'] = 'https'
        return app(environ, start_response)

    return wrapper


http_server = WSGIServer(("0.0.0.0", 3000), _force_https(server))
logger.info("Server started on port 3000")
http_server.serve_forever()