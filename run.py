from gevent.pywsgi import WSGIServer
from engine.server import server


def _force_https(app):
    def wrapper(environ, start_response):
        # environ['wsgi.url_scheme'] = 'https'
        return app(environ, start_response)

    return wrapper


server = _force_https(server)

http_server = WSGIServer(("0.0.0.0", 3000), server)
http_server.serve_forever()
