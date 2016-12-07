import os
import gdal, osr
from thread import allocate_lock
import mapnik

try:
    from PIL import Image
except ImportError:
    # On some systems, PIL.Image is known as Image.
    import Image

if 'mapnik' in locals():
    _version = hasattr(mapnik, 'mapnik_version') and mapnik.mapnik_version() or 701

    if _version >= 20000:
        Box2d = mapnik.Box2d
    else:
        Box2d = mapnik.Envelope

global_mapnik_lock = allocate_lock()


DEFAULT_MAP_SRS = "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 " + \
    "+lon_0=0.0 +x_0=0.0 +y_0=0.0 +k=1.0 +units=m " +\
    "+nadgrids=@null +wktext +no_defs +over"


class MapnikPythonProvider(object):
    def __init__(self, layer, **kwargs):
        self.layer = layer
        self.filepath = kwargs.pop("path", None)
        self.map_srs = kwargs.pop("map_srs", DEFAULT_MAP_SRS)
        self.scale_factor = None
        self._layer_srs = None

    @property
    def layer_srs(self):
        if self._layer_srs is None:
            raster = gdal.Open(self.filepath)
            srs = osr.SpatialReference()
            srs.ImportFromWkt(raster.GetProjectionRef())
            self._layer_srs = srs.ExportToProj4()

        return self._layer_srs


    def style_map(self, Map):
        #<Map font-directory="./fonts" srs="{{map_srs}}">
        #  <Layer name="raster-layer" srs="{{layer_srs}}" status="on">
        #    <StyleName>raster-style</StyleName>
        #    <Datasource>
        #      <Parameter name="type">gdal</Parameter>
        #      <Parameter name="file">{{ filepath }}</Parameter>
        #      <Parameter name="format">tiff</Parameter>
        #      <Parameter name="band">4</Parameter>
        #    </Datasource>
        #  </Layer>
        #  <Style name="raster-style">
        #    <Rule>
        #      <RasterSymbolizer
        #         opacity="0.8">
        #      <RasterColorizer default-mode="linear" default-color="white" epsilon="0.001">
        #        <stop color="blue"        value = "-1"   />
        #        <stop color="beige"       value = "0"    />
        #        <stop color="green"       value = "1"    />
        #      </RasterColorizer>
        #       <!-- optinal <RasterColorizer/> goes here -->
        #      </RasterSymbolizer>
        #    </Rule>
        #  </Style>
        #</Map>
        style = mapnik.Style()
        rule = mapnik.Rule()
        sym = mapnik.RasterSymbolizer()
        sym.opacity = 0.8

        colorizer = mapnik.RasterColorizer(
            mapnik.COLORIZER_LINEAR,
            mapnik.Color("white")
        )
        colorizer.epsilon = 0.001

        colorizer.add_stop(-1, mapnik.Color("blue"))
        colorizer.add_stop(0, mapnik.Color("beige"))
        colorizer.add_stop(1, mapnik.Color("green"))

        sym.colorizer = colorizer
        rule.symbols.append(sym)
        style.rules.append(rule)

        Map.append_style('Raster Style', style)

        lyr = mapnik.Layer('GDAL Layer from TIFF', self.layer_srs)

        lyr.datasource = mapnik.Gdal(base=os.path.dirname(self.filepath),
                                     file=os.path.basename(self.filepath),\
                                     format="tiff",
                                     band=4)
        lyr.styles.append("Raster Style")

        Map.layers.append(lyr)

        return Map

    def renderArea(self, width, height, srs, xmin, ymin, xmax, ymax, zoom):
        """
        """

        # NB: To be thread-safe Map object cannot be stored as apart
        #     of the class, see: https://groups.google.com/forum/#!topic/mapnik/USDlVfSk328

        Map = mapnik.Map(width, height, self.map_srs)
        Map.zoom_to_box(Box2d(xmin, ymin, xmax, ymax))

        Map = self.style_map(Map)

        img = mapnik.Image(width, height)
        # Don't even call render with scale factor if it's not
        # defined. Plays safe with older versions.
        if self.scale_factor is None:
            mapnik.render(Map, img)
        else:
            mapnik.render(Map, img, self.scale_factor)

        img = Image.frombytes('RGBA', (width, height), img.tostring())

        return img
