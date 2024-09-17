import configparser
from falcon import App
from core.Utils import Utils, logger


class RouteLoader:
    def __init__(self, server):
        self._server: App = server
        self._registry = {}
        self.config = configparser.ConfigParser()
        self.config.read(Utils.get_config_ini_file_path())
        self.context_from_config = self.config.get('ROUTES', 'context')
        self.context_prefix = f"/{self.context_from_config}" if self.context_from_config != '' else ''

    def __call__(self, route, suffix=None):
        def decorator(cls):
            instance = self._registry.get(cls)
            if instance is None:
                instance = self._registry[cls] = cls()
            self._server.add_route(self.context_prefix + route, instance, suffix=suffix)
            logger.info(f"Route: {self.context_prefix + route}, {instance}, suffix={suffix} ")
            return cls

        return decorator