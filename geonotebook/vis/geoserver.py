import requests
import os

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

        self.base_url = url
        self.c = Client(self.base_url + "/rest", username=username, password=password)

    def process(self, data_path, name=None):
        # Should pull workspace from config probably
        workspace = 'test'

        if name is None:
            name = os.path.splitext(os.path.basename(data_path))[0]

        # Create the workspace
        self.c.post("/workspaces.json",
                    json={'workspace': {'name': workspace}})

        # Upload the file and convert it to a coveragestore etc
        with open(data_path, 'rb') as fh:
            self.c.put("/workspaces/{}/coveragestores/{}/file.geotiff".format(workspace, name),
                       params={"coverageName": name,
                               "configure": "all"},
                       headers={"Content-type": "image/tiff"},
                       data=fh)

        # Tweak some properties
        current = self.c.get("/workspaces/test/coveragestores/rgb/coverages/rgb.json").json()

        current['coverage']['dimensions']['coverageDimension'][0]['nullValues']['double'][0] = -32768
        current['coverage']['dimensions']['coverageDimension'][0]['range']['min'] = 0
        current['coverage']['dimensions']['coverageDimension'][0]['range']['max'] = 0.4
        current['coverage']['dimensions']['coverageDimension'][1]['nullValues']['double'][0] = -32768
        current['coverage']['dimensions']['coverageDimension'][1]['range']['min'] = 0
        current['coverage']['dimensions']['coverageDimension'][1]['range']['max'] = 0.4
        current['coverage']['dimensions']['coverageDimension'][2]['nullValues']['double'][0] = -32768
        current['coverage']['dimensions']['coverageDimension'][2]['range']['min'] = 0
        current['coverage']['dimensions']['coverageDimension'][2]['range']['max'] = 0.4

        self.c.put("/workspaces/test/coveragestores/rgb/coverages/rgb.json", json=current)

        return self.base_url + "/ows"
