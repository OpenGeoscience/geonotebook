from geonotebook.wrappers import RasterData
from sld import get_single_band_raster_sld, get_multiband_raster_sld
import matplotlib as mpl
from matplotlib import pylab as plt
import numpy as np
import requests
import os

class Client(object):
    def __init__(self, url, username='admin', password='geoserver'):
        self.base_url = url
        self.auth = {'auth': (username, password)}

    def _proxy(self, method, uri, *args, **kwargs):
        kwargs.update(self.auth)
        if uri.startswith("http"):
            return method(uri, *args, **kwargs)
        else:
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

    def __init__(self, url=None, username="admin",
                 password="geoserver", workspace="test"):
        assert url is not None, \
            "Must pass in a URL to Geoserver instance!"
        self.workspace = workspace
        self.base_url = url
        self.c = Client(self.base_url + "/rest", username=username,
                        password=password)

    @property
    def coverage_stores(self):
        r = self.c.get("/workspaces/{}/coveragestores.json".format(self.workspace))

        if r.status_code == 200:
            try:
                # probably need better error checking here
                cs = r.json()['coverageStores']['coverageStore']
            except Exception:
                cs = []

            return {store['name']: store['href'] for store in cs}
        else:
            return None

    def coverages(self, store):

        if store in self.coverage_stores:
            uri = "/workspaces/{}/coveragestores/{}/coverages.json"
            r = self.c.get(uri.format(self.workspace, store))

            if r.status_code == 200:
                try:
                    coverages = r.json()['coverages']['coverage']
                except Exception:
                    coverages = []

                return {c['name']: c['href'] for c in coverages}
            else:
                return {}
        else:
            return {}

    @staticmethod
    def generate_colormap(viz_params, minimum, maximum):
        """ Viz_params can be a list of dicts
        or a matplotlib colormap. Either case
        the returned object will be a list of dicts.
        """

        # If viz_params is None use a default colormap (e.g. matplotlib.pylab.cm.jet)
        # and transform it into the list of colormap entry dicts
        if viz_params == None:
            cmap = plt.get_cmap('jet', 10)
            colormap = [{"color": mpl.colors.rgb2hex(cmap(i)), "quantity": v }
                        for i,v in zip(range(cmap.N),np.linspace(minimum, maximum, cmap.N))]

            return colormap
        # if viz_params is a matplotlib colormap,
        # transform that into the list of colormap entry dicts
        elif isinstance(viz_params, (str, unicode)):
            cmap = plt.get_cmap(viz_params, 10)
            colormap = [{"color": mpl.colors.rgb2hex(cmap(i)), "quantity": v }
                        for i,v in zip(range(cmap.N),np.linspace(minimum, maximum, cmap.N))]

            return colormap

        # if viz_params is a list of dicts, pass it through to
        # get_single_band_raster_sld
        if all(isinstance(viz_param, dict) for viz_param in viz_params):
            return viz_params


    # get_params should take a generic list of paramaters e.g. 'bands',
    # 'range', 'gamma' and convert these into a list of vis_server specific
    # paramaters which will be passed along to the tile render handler in
    # add_layer. This is intended to allow the vis_server to include style
    # paramaters and subsetting operations. select bands, set ranges
    # on a particular dataset etc.
    def get_params(self, name, data, **kwargs):
        if data is not None:
            name = "{}:{}".format(self.workspace, name)
            options = {}
            if len(data) == 1:
                options['band'] = data.band_indexes[0]

                if 'colormap' not  in kwargs:
                    viz_params = None
                else:
                    viz_params = kwargs['colormap']

                cmap = self.generate_colormap(viz_params, data.min, data.max)

                options.update(kwargs)
                options['colormap'] = cmap

                sld_body = get_single_band_raster_sld(name, **options)
            else:
                options['bands'] = data.band_indexes
                options['range'] = zip(data.min, data.max)

                options.update(kwargs)

                sld_body = get_multiband_raster_sld(name, **options)

            return {"SLD_BODY": sld_body}
        else:
            return kwargs


    def _process_raster(self, name, data):
        # Note: coverage stores and coverages currently
        # always have the same name
        coverages = self.coverages(name)

        if name not in coverages:
            # Upload the file and convert it to a coveragestore etc
            with open(data.path, 'rb') as fh:
                uri = "/workspaces/{}/coveragestores/{}/file.geotiff"
                self.c.put(uri.format(self.workspace, name),
                           params={"coverageName": name,
                                   "configure": "all"},
                           headers={"Content-type": "image/tiff"},
                           data=fh)

# This code path could be used to tweak raster properties once it was uploaded
# Curently we don't need to do this,  but i'm keeping it here for reference
#             r = self.c.get(self.coverages[name])
#         else:
#             r = self.c.get(coverages[name])
#
#         if r.status_code == 200:
#             current = r.json()
#             # TWEAK PROPERTIES HERE

#             self.c.put(coverages[name], json=current)
#         else:
#             # Raise exception
#             pass

        return self.base_url + "/ows?LAYERS={}".format(name)

    # The purpose of the 'ingest' endpoint is to get a file (e.g. as
    # represented by a RasterData object) and move it into whatever
    # system is going to actually render tiles.  It should not rely on
    # any subsetting or style info - it is not designed, for instance, to make
    # specific bands available on the tile server, it is about (as needed)
    # transfering bytes from a source location (data.path) to a destination
    # Defined as apart of the vis_server config along with any metadata
    # Needed to geospatially reference the data on the remote system
    def ingest(self, data, name=None):

        name = data.name if name is None else name

        # Create the workspace

        r = self.c.post("/workspaces.json",
                        json={'workspace': {'name': self.workspace}})

        if r.status_code != 201:
            # Log warning?
            pass

        if isinstance(data, RasterData):
            return self._process_raster(name, data)

        # elif isinstance(data, VectorData):
        #     pass

        else:
            # Raise Error
            pass
