import logging
import logging.handlers

from notebook.base.handlers import IPythonHandler
import requests


class LoggingRequestHandler(IPythonHandler):
    """Handles incoming requests to the /log endpoint of the notebook."""

    def check_xsrf_cookie(self):
        return True

    def post(self):
        self.log.handle(logging.makeLogRecord(self.get_json_body()))


class JsonHTTPHandler(logging.handlers.HTTPHandler):
    """Handles sending logs over HTTP in a JSON format.

    Example Usage:
    >>> import logging
    >>> logger = logging.getLogger('example_log')
    >>> logger.addHandler(JsonHTTPHandler('http://localhost:8888', '/log'))
    >>> logger.info('Informational logging message')
    """

    def __init__(self, host, url):
        return super(JsonHTTPHandler, self).__init__(host, url, 'POST')

    def emit(self, record):
        try:
            record = self.mapLogRecord(record)
            requests.post(self.host + self.url, json=record)
        except Exception:
            self.handleError(record)
