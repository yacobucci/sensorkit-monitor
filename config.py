import os
from typing import Any
import yaml

def load_config(filename: str) -> dict[str, Any]:
    exp = os.path.expandvars(filename)
    with open(exp, 'r') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    return data

class Config:
    def __init__(self, config: dict[str, Any]):
        self._data = config

        self._host = None
        self._port = None

        self._log_destination = None
        self._log_level       = None
        self._log_format      = None

        self._metrics_endpoint = None
        self._metrics_encoding = None
        self._metrics_labels = None

    @property
    def host(self):
        if self._host is not None:
            return self._host

        try:
            self._host = self._data['app']['listen']['host']
        except KeyError:
            self._host = '127.0.0.1'
        return self._host

    @property
    def port(self):
        if self._port is not None:
            return self._port

        try:
            self._port = int(self._data['app']['listen']['port'])
        except KeyError:
            self._port = 8080
        return self._port

    @property
    def log_destination(self):
        if self._log_destination is not None:
            return self._log_destination

        try:
            logging = self._data['app']['logging']
        except KeyError as e:
            message = 'config must have logging section to configure logger - missing {}'
            raise AttributeError(message.format(e))

        self._log_destination = logging.get('destination', 'sys.stdout')
        return self._log_destination

    @property
    def log_level(self):
        if self._log_level is not None:
            return self._log_level

        try:
            logging = self._data['app']['logging']
        except KeyError as e:
            message = 'config must have logging section to configure logger - missing {}'
            raise AttributeError(message.format(e))

        self._log_level = logging.get('log-level', 'info')
        return self._log_level

    @property
    def log_format(self):
        if self._log_format is not None:
            return self._log_format

        try:
            logging = self._data['app']['logging']
        except KeyError as e:
            message = 'config must have logging section to configure logger - missing {}'
            raise AttributeError(message.format(e))

        self._log_format = logging.get('format', '%(levelname)s %(asctime)s %(message)s')
        return self._log_format

    @property
    def metrics_endpoint(self):
        if self._metrics_endpoint is not None:
            return self._metrics_endpoint

        try:
            metrics = self._data['app']['metrics']
        except KeyError as e:
            message = 'config must have metrics to export data - missing {}'
            raise AttributeError(message.format(e))

        self._metrics_endpoint = metrics.get('endpoint', '/metrics')
        return self._metrics_endpoint

    @property
    def metrics_encoding(self):
        if self._metrics_encoding is not None:
            return self._metrics_encoding

        encoding = None
        try:
            metrics = self._data['app']['metrics']
            encoding = metrics['encoding']
        except KeyError as e:
            message = 'config must have metrics.encoding to export data - missing {}'
            raise AttributeError(message.format(e))

        self._metrics_encoding = encoding
        return self._metrics_encoding

    @property
    def metrics_labels(self):
        if self._metrics_labels is not None:
            return self._metrics_labels

        try:
            metrics = self._data['app']['metrics']
        except KeyError as e:
            message = 'config must have metrics to export data - missing {}'
            raise AttributeError(message.format(e))
 
        self._metrics_labels = metrics.get('labels', {})
        return self._metrics_labels
