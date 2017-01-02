from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import json

from ModestMaps.Core import Coordinate
from notebook.base.handlers import IPythonHandler
from tornado import concurrent, ioloop
from tornado import gen
from tornado import web

from .utils import serialize_config, serialize_layer


class KTileAsyncClient(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(
                KTileAsyncClient, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.io_loop = ioloop.IOLoop.current()

    @concurrent.run_on_executor
    def getTileResponse(self, layer, coord, extension,
                        _debug=False, _profile=False):
        if _debug:
            from pudb.remote import set_trace; set_trace(term_size=(255, 70)) # noqa

        if _profile:
            # profile injected by kernprof
            output = layer.getTileResponse(coord, extension)
            return output

        return layer.getTileResponse(coord, extension)


class KtileHandler(IPythonHandler):

    def check_xsrf_cookie(self):
        # TODO: Find a way to correctly communicate XSRF secret to
        #       the kernel so ingest requests can be property authenticated
        pass

    def initialize(self, ktile_config_manager):
        self.ktile_config_manager = ktile_config_manager

        try:
            if self.request.headers["Content-Type"].startswith(
                    "application/json"):
                self.request.json = json.loads(self.request.body)
        except Exception:
            self.request.json = None

    def post(self, kernel_id):
        # Note:  needs paramater validation
        kwargs = {} if self.request.json is None else self.request.json

        self.ktile_config_manager.add_config(kernel_id, **kwargs)
        self.log.info("Created config for {}".format(kernel_id))
        self.finish()

    def delete(self, kernel_id):
        try:
            del self.ktile_config_manager[kernel_id]
        except KeyError:
            raise web.HTTPError(404, u'Kernel %s not found' % kernel_id)

    def get(self, kernel_id, **kwargs):
        try:
            config = self.ktile_config_manager[kernel_id]
        except KeyError:
            raise web.HTTPError(404, u'Kernel %s not found' % kernel_id)

        self.finish(serialize_config(config))


class KtileLayerHandler(IPythonHandler):
    def check_xsrf_cookie(self):
        # TODO: Find a way to correctly communicate XSRF secret to
        #       the kernel so ingest requests can be property authenticated
        pass

    def initialize(self, ktile_config_manager):
        self.ktile_config_manager = ktile_config_manager

    def prepare(self):
        try:
            if self.request.headers["Content-Type"].startswith(
                    "application/json"):
                self.request.json = json.loads(self.request.body)
        except Exception:
            self.request.json = None

    def post(self, kernel_id, layer_name):
        # Note: needs paramater validation
        try:
            self.ktile_config_manager.add_layer(
                kernel_id, layer_name, self.request.json)

            self.write({'status': 1})

        except Exception:
            import sys
            import traceback
            t, v, tb = sys.exc_info()

            self.log.error(''.join(traceback.format_exception(t, v, tb)))

            self.write({'status': 0,
                        'error': traceback.format_exception(t, v, tb)})

    def get(self, kernel_id, layer_name, **kwargs):
        try:
            layer = self.ktile_config_manager[kernel_id].layers[layer_name]
        except KeyError:
            raise web.HTTPError(404, u'Kernel %s not found' % kernel_id)

        self.finish(serialize_layer(layer))


class KtileTileHandler(IPythonHandler):

    def initialize(self, ktile_config_manager):
        self.client = KTileAsyncClient()
        self.ktile_config_manager = ktile_config_manager

    @gen.coroutine
    def get(self, kernel_id, layer_name, x, y, z, extension, **kwargs):
        _debug = self.get_query_argument("debug", default=False)
        _profile = self.get_query_argument("profile", default=False)

        if _debug:
            import pudb, pu.db # noqa

        config = self.ktile_config_manager[kernel_id]

        layer = config.layers[layer_name]
        coord = Coordinate(int(y), int(x), int(z))

        status_code, headers, content = yield self.client.getTileResponse(
            layer, coord, extension,
            _debug=_debug, _profile=_profile)

        if layer.max_cache_age is not None:
            expires = datetime.utcnow() + timedelta(
                seconds=layer.max_cache_age)
            headers['Expires'] = expires.strftime('%a %d %b %Y %H:%M:%S GMT')
            headers['Cache-Control'] = 'public, max-age=%d' \
                % layer.max_cache_age
        else:
            headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            headers['Pragma'] = 'no-cache'
            headers['Expires'] = '0'

        # Force allow cross origin access
        headers["Access-Control-Allow-Origin"] = "*"

        # Fill tornado handler properties with ktile code/header/content
        for k, v in headers.items():
            self.set_header(k, v)

        self.set_status(status_code)

        self.write(content)
