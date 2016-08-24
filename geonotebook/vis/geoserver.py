import requests


class Client(object):
    def __init__(self, url, username='admin', password='geoserver'):
        self.base_url = url
        self.auth = {'auth': (username, password)}

    def _proxy(self, method, uri, *args, **kwargs):
        kwargs.update(self.auth)
        return method(self.base_url + uri, *args, **kwargs)

    def get(self, *args, **kwargs):
        return self._proxy(requests.get, *args, **kwargs)

    def put(self, *args, **kwargs):
        return self._proxy(requests.put, *args, **kwargs)

    def post(self, *args, **kwargs):
        return self._proxy(requests.post, *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self._proxy(requests.delete, *args, **kwargs)

    def head(self, *args, **kwargs):
        return self._proxy(requests.head, *args, **kwargs)


class Geoserver(object):

    def __init__(self, url=None, username="admin", password="geoserver"):
        assert url is not None, \
            "Must pass in a URL to Geoserver instance!"

        self.c = Client(url, username=username, password=password)

    def process(self, data_path):
        pass
