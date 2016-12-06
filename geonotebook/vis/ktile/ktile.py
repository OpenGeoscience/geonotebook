import os
import requests
from notebook.utils import url_path_join as ujoin
from .handler import (KtileHandler,
                      KtileLayerHandler,
                      KtileTileHandler,
                      GeoJSTestHandler)
from .config import KtileConfig, KtileLayerConfig
from collections import MutableMapping


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
        if not isinstance(value, KtileConfig):
            raise RuntimeError(
                "{} only accepts objects of type {}".format(
                    self.__class__.__name__, KtileConfig.__class__.__name__))

        if value.cache is None:
            value.cache = self.default_cache

        self._configs.__setitem__(_id, value)

    def __delitem__(self, *args, **kwargs):
        return self._configs.__delitem__(*args, **kwargs)

    def __iter__(self, *args, **kwargs):
        return self._configs.__iter__(*args, **kwargs)

    def __len__(self, *args, **kwargs):
        return self._configs.__len__(*args, **kwargs)

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

            # Debug
            (ujoin(base_url, r"/test/([^/]*)/([^/]*)"), GeoJSTestHandler)

        ])


    # get_params should take a generic list of parameters e.g. 'bands',
    # 'range', 'gamma' and convert these into a list of vis_server specific
    # parameters which will be passed along to the tile render handler in
    # add_layer. This is intended to allow the vis_server to include style
    # parameters and subsetting operations. select bands, set ranges
    # on a particular dataset etc.
    def get_params(self, name, data, **kwargs):
        kernel_id = kwargs.pop("kernel_id")

        return kwargs

    # The purpose of the 'ingest' endpoint is to get a file (e.g. as
    # represented by a RasterData object) and move it into whatever
    # system is going to actually render tiles.  It should not rely on
    # any subsetting or style info - it is not designed, for instance, to make
    # specific bands available on the tile server, it is about (as needed)
    # transfering bytes from a source location (data.path) to a destination
    # Defined as apart of the vis_server config along with any metadata
    # Needed to geospatially reference the data on the remote system
    def ingest(self, data, name=None, **kwargs):
        # from pudb.remote import set_trace; set_trace(term_size=(283,87))
        name = data.name if name is None else name

        kernel_id = kwargs.pop('kernel_id', None)

        if kernel_id is None:
            raise Exception("Must pass in kernel_id as kwarg to ingest!")

        base_url = '{}/{}/{}'.format(self.base_url, kernel_id, name)

        r = requests.post(
            base_url, json={"name": name,
                            "path": os.path.abspath(data.path),
                            "bands": data.band_indexes})

        return base_url
