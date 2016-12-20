import os
import requests
from notebook.utils import url_path_join as ujoin
from .handler import (KtileHandler,
                      KtileLayerHandler,
                      KtileTileHandler)
from collections import MutableMapping
from ..utils import generate_colormap

import TileStache as ts
# NB:  this uses a 'private' API for parsing the Config layer dictionary
from TileStache.Config import _parseConfigLayer as parseConfigLayer


# Manage kernel_id => layer configuration section
# Note - when instantiated this is a notebook-wide class,
# it manages the configuration for all running geonotebook
# kernels. It lives inside the Tornado Webserver
class KtileConfigManager(MutableMapping):
    def __init__(self, default_cache, *args, **kwargs):
        self.default_cache = default_cache
        self._configs = {}

    def __getitem__(self, *args, **kwargs):
        return self._configs.__getitem__(*args, **kwargs)

    def __setitem__(self, _id, value):
        self._configs.__setitem__(_id, value)

    def __delitem__(self, *args, **kwargs):
        return self._configs.__delitem__(*args, **kwargs)

    def __iter__(self, *args, **kwargs):
        return self._configs.__iter__(*args, **kwargs)

    def __len__(self, *args, **kwargs):
        return self._configs.__len__(*args, **kwargs)

    def add_config(self, kernel_id, **kwargs):
        cache = kwargs.get("cache", self.default_cache)

        self._configs[kernel_id] = ts.parseConfig({
            "cache": cache,
            "layers": {}
        })

    def add_layer(self, kernel_id, layer_name, layer_dict, dirpath=''):
        # NB: dirpath is actually not used in _parseConfigLayer So dirpath
        # should have no effect regardless of its value.

        # Note: Needs error checking
        layer = parseConfigLayer(layer_dict, self._configs[kernel_id], dirpath)

        self._configs[kernel_id].layers[layer_name] = layer

        return layer.provider.generate_vrt()


# Ktile vis_server,  this is not a persistent object
# It is brought into existence as a client to provide access
# to the KtileConfigManager through the Tornado webserver's
# REST API vi ingest/get_params. It is instantiated once inside
# the tornado app in order to call initialize_webapp.  This sets
# up the REST API that ingest/get_params communicate with. It also
# provides access points to start_kernel and shutdown_kernel for
# various initialization. NB: State CANNOT be shared across these
# different contexts!

class Ktile(object):
    def __init__(self, config, url=None, default_cache=None):
        self.config = config
        self.base_url = url
        self.default_cache_section = default_cache

    @property
    def default_cache(self):
        return dict(self.config.items(self.default_cache_section))


    def start_kernel(self, kernel):
        requests.post("{}/{}".format(self.base_url, kernel.ident))
        # Error checking on response!

    def shutdown_kernel(self, kernel):
        requests.delete("{}/{}".format(self.base_url, kernel.ident))
        pass

    # This function is caleld inside the tornado web app
    # from jupyter_load_server_extensions
    def initialize_webapp(self, config, webapp):
        base_url = webapp.settings['base_url']


        webapp.ktile_config_manager = KtileConfigManager(
            self.default_cache)

        webapp.add_handlers('.*$', [
            # kernel_name
            (ujoin(base_url, r'/ktile/([^/]*)'),
             KtileHandler,
             dict(ktile_config_manager=webapp.ktile_config_manager)),

            # kernel_name, layer_name
            (ujoin(base_url, r'/ktile/([^/]*)/([^/]*)'),
             KtileLayerHandler,
             dict(ktile_config_manager=webapp.ktile_config_manager)),

            # kernel_name, layer_name, x, y, z, extension
            (ujoin(base_url,
                   r'/ktile/([^/]*)/([^/]*)/([^/]*)/([^/]*)/([^/\.]*)\.(.*)'),
             KtileTileHandler,
             dict(ktile_config_manager=webapp.ktile_config_manager)),

        ])


    # get_params should take a generic list of parameters e.g. 'bands',
    # 'range', 'gamma' and convert these into a list of vis_server specific
    # parameters which will be passed along to the tile render handler in
    # add_layer. This is intended to allow the vis_server to include style
    # parameters and subsetting operations. select bands, set ranges
    # on a particular dataset etc.
    def get_params(self, name, data, **kwargs):
        # All paramater setup is handled on ingest
        return {}

    # The purpose of the 'ingest' endpoint is to get a file (e.g. as
    # represented by a RasterData object) and move it into whatever
    # system is going to actually render tiles.  It should not rely on
    # any subsetting or style info - it is not designed, for instance, to make
    # specific bands available on the tile server, it is about (as needed)
    # transfering bytes from a source location (data.path) to a destination
    # Defined as apart of the vis_server config along with any metadata
    # Needed to geospatially reference the data on the remote system
    def ingest(self, data, name=None, **kwargs):

        kernel_id = kwargs.pop('kernel_id', None)
        if kernel_id is None:
            raise Exception("KTile vis server requires kernel_id as kwarg to ingest!")

        name = data.name if name is None else name


        options = {}

        # Metadata

        options['name'] = name

        # VRT options

        options['path'] = os.path.abspath(data.path)
        options['bands'] = data.band_indexes

        options['nodata'] = data.nodata

        # TODO:  Needs to be moved into RasterData level API
        options['raster_x_size'] = data.reader.width
        options['raster_y_size'] = data.reader.height

        # TODO:  Needs to be moved into RasterData level API
        options['transform'] = data.reader.dataset.profile['transform']
        options['dtype'] = data.reader.dataset.profile['dtype']

        if 'vrt_path' in kwargs:
            options['vrt_path'] = kwargs['vrt_path']



        # Style Options

        options['opacity'] = kwargs.get("opacity", 1)
        options['gamma'] = kwargs.get("gamma", 1)



        if len(data.band_indexes) == 1:
            try:
                # If we have the colormap in the form
                # of a list of dicts with color/quantity then
                # set options['colormap'] equal to this
                for d in kwargs.get("colormap", None):
                    assert 'color' in d
                    assert 'quantity' in d
                options['colormap'] = kwargs.get('colormap')

            except:
                # Otherwise try to figure out the correct colormap
                # using data min/max
                _min = kwargs.get('min', data.min)
                _max = kwargs.get('max', data.max)

                options['colormap'] = generate_colormap(
                    kwargs.get('colormap', None), _min, _max)

        # Make the Request

        base_url = '{}/{}/{}'.format(self.base_url, kernel_id, name)

        r = requests.post(base_url, json={
            "provider": {
                "class": "geonotebook.vis.ktile.provider:MapnikPythonProvider",
                "kwargs": options
            }
            # NB: Other KTile layer options could go here
            #     See: http://tilestache.org/doc/#layers
        })

        if r.json()['status'] == 0:
            raise RuntimeError("KTile.ingest() returned error:\n\n{}".format(
                ''.join(r.json()['error'])))

        return base_url
