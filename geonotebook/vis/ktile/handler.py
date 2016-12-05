from tornado import web
from notebook.base.handlers import IPythonHandler
from datetime import datetime, timedelta
import TileStache as ts
from ModestMaps.Core import Coordinate
from jinja2 import Template
from .config import KtileConfig


def get_config():
    config = {
        "cache":
        {
            "name": "Test",
            "path": "/tmp/stache",
            "umask": "0000"
        },
        "layers":
        {
            "osm":
            {
                "provider": {"name": "proxy", "provider": "OPENSTREETMAP"},
                "png options": {
                    "palette":
                    "http://tilestache.org/" +
                    "example-palette-openstreetmap-mapnik.act"
                }
            },
            "example":
            {
                "provider":
                {"name": "mapnik",
                 "mapconfig": "/home/kotfic/src/KTile/examples/style.xml"},
                "projection": "spherical mercator"
            }
        }
    }

    return config


class KtileHandler(IPythonHandler):
    def initialize(self, ktile_config_manager):
        self.ktile_config_manager = ktile_config_manager

    def post(self, kernel_id):
        self.ktile_config_manager[kernel_id] = KtileConfig()

    def delete(self, kernel_id):
        try:
            del self.ktile_config_manager[kernel_id]
        except KeyError:
            raise web.HTTPError(404, u'Kernel %s not found' % kernel_id)

    def get(self, kernel_id, **kwargs):
        try:
            self.finish(self.ktile_config_manager[kernel_id].config)
        except KeyError:
            raise web.HTTPError(404, u'Kernel %s not found' % kernel_id)


class KtileLayerHandler(IPythonHandler):
    def initialize(self, ktile_config_manager):
        self.ktile_config_manager = ktile_config_manager

    def get(self, kernel_name, layer_name, **kwargs):
        self.ktile_config_manager.test += 1
        self.finish(self.ktile_config_manager.test)


class KtileTileHandler(IPythonHandler):

    def initialize(self, ktile_config_manager):
        self.ktile_config_manager = ktile_config_manager

    def get(self, kernel_name, layer_name, x, y, z, extension, **kwargs):
        # from pudb.remote import set_trace; set_trace(term_size=(319,87))
        config = ts.parseConfig(get_config())

        layer = config.layers[layer_name]
        coord = Coordinate(int(y), int(x), int(z))

        status_code, headers, content = layer.getTileResponse(coord, extension)

        if layer.max_cache_age is not None:
            expires = datetime.utcnow() + timedelta(
                seconds=layer.max_cache_age)
            headers.setdefault(
                'Expires', expires.strftime('%a %d %b %Y %H:%M:%S GMT'))
            headers.setdefault(
                'Cache-Control', 'public, max-age=%d' % layer.max_cache_age)

        # Force allow cross origin access
        headers["Access-Control-Allow-Origin"] = "*"

        # Fill tornado handler properties with ktile code/header/content
        for k, v in headers.items():
            self.set_header(k, v)

        self.set_status(status_code)

        self.write(content)

# Debug Code


class GeoJSTestHandler(IPythonHandler):
    template = Template("""
    <head>
    <script src="/nbextensions/geonotebook/lib/geo.js"></script>


    <style>
        html, body, #map {
            margin: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
        }
    </style>

    <script>
    $(function () {
            var map = geo.map({'node': '#map'});
            var layer = map.createLayer('osm', {
'keepLower': false,
'url': 'http://192.168.30.110:8888/ktile/{{kernel_id}}/{{layer_name}}/{x}/{y}/{z}.png'
            });

    });
    </script>
    </head>
    <body>
    <div id="map"></div>
    </body>
    """)

    def get(self, kernel_id, layer_name, *args, **kwargs):
        self.finish(
            self.template.render({"layer_name": layer_name,
                                  "kernel_id": kernel_id})
        )
