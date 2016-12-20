import os
import tempfile
import gdal, osr
from thread import allocate_lock
import mapnik

from .vrt import *

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


DEFAULT_MAP_SRS = 'EPSG:4326'

class MapnikPythonProvider(object):
    numpy_to_vrt_type = {
        'uint8': 'Byte'
    }

    def __init__(self, layer, **kwargs):
        # List of bands to display,  should be len == 1 or len == 3
        self._bands = kwargs.get('bands', -1)
        self._last_hash = None

        self._static_vrt = kwargs.get("vrt_path", None)

        if self._static_vrt is None:
            #self._vrt_path = os.path.join(
            #    tempfile.mkdtemp(), '{}.vrt'.format(kwargs.get('name', 'no_name')))
            self._vrt_path = "/tmp/geonotebook/{}.vrt".format(kwargs.get('name', 'no_name'))

        self._filepath = None

        self.layer = layer

        self.filepath = kwargs.get('path', None)
        self.map_srs = kwargs.get('map_srs', DEFAULT_MAP_SRS)

        self.name = kwargs.get('name', None)


        self.raster_x_size = kwargs.get('raster_x_size', None)
        self.raster_y_size = kwargs.get('raster_y_size', None)


        self.transform = kwargs.get('transform', None)

        self.nodata = float(kwargs.get('nodata', None))

        try:
            self.dtype = self.numpy_to_vrt_type[kwargs['dtype']]
        except KeyError:
            self.dtype = None

        # The band value mapnik expects
        self.band = -1 if len(self._bands) == 3 else self._bands[0]

        self.opacity = kwargs.get('opacity', 1)
        self.gamma = kwargs.get('gamma', 1)

        self.colormap = kwargs.get('colormap', None)

        self.scale_factor = None




    def __hash__(self):
        return hash((
            self.filepath,
            self.map_srs,
            self.name,
            tuple(self._bands),
            self.opacity,
            self.gamma,
            self.nodata,
            tuple(tuple(cm.items()) for cm in self.colormap),
            self.scale_factor))


    def generate_vrt(self):
        if self._static_vrt is not None:
            return

        vrt = VRTDataset(rasterXSize = self.raster_x_size,
                         rasterYSize = self.raster_y_size)
        vrt.SRS = [self.map_srs]
        vrt.GeoTransform = [", ".join([str(f) for f in self.transform])]

        for b in self._bands:
            vrt_band = VRTRasterBandType(dataType=self.dtype,
                                         NoDataValue=[self.nodata],
                                         ComplexSource=[
                                             ComplexSourceType(
                                                 NODATA=self.nodata,
                                                 SourceFilename=[
                                                     SourceFilenameType(
                                                         relativeToVRT=0,
                                                         valueOf_=self.filepath)],
                                                 SourceBand=[b])
                                         ])

            vrt.VRTRasterBand.append(vrt_band)


        with open(self._vrt_path, 'w') as fh:
            vrt.export(fh, 0)

        return self._vrt_path


    @property
    def vrt_path(self):
        if self._static_vrt is not None:
            return self._static_vrt

        if self._last_hash != hash(self):
            self.generate_vrt()
            self._last_hash = hash(self)

        return self._vrt_path


    @property
    def filepath(self):
        return self._filepath

    @filepath.setter
    def filepath(self, val):
        if val != self._filepath:
            self._layer_srs = None

        self._filepath = val


    @property
    def layer_srs(self):
        if self._layer_srs is None:
            # TODO: Hard-coded
            self._layer_srs = "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs "

        return self._layer_srs


    def style_map(self, Map):
        #<Map font-directory='./fonts' srs='{{map_srs}}'>
        #  <Layer name='raster-layer' srs='{{layer_srs}}' status='on'>
        #    <StyleName>raster-style</StyleName>
        #    <Datasource>
        #      <Parameter name='type'>gdal</Parameter>
        #      <Parameter name='file'>{{ filepath }}</Parameter>
        #      <Parameter name='format'>tiff</Parameter>
        #      <Parameter name='band'>4</Parameter>
        #    </Datasource>
        #  </Layer>
        #  <Style name='raster-style'>
        #    <Rule>
        #      <RasterSymbolizer
        #         opacity='0.8'>
        #      <RasterColorizer default-mode='linear' default-color='white' epsilon='0.001'>
        #        <stop color='blue'        value = '-1'   />
        #        <stop color='beige'       value = '0'    />
        #        <stop color='green'       value = '1'    />
        #      </RasterColorizer>
        #       <!-- optinal <RasterColorizer/> goes here -->
        #      </RasterSymbolizer>
        #    </Rule>
        #  </Style>
        #</Map>

        style = mapnik.Style()
        rule = mapnik.Rule()

        sym = mapnik.RasterSymbolizer()
        sym.opacity = self.opacity

        colorizer = mapnik.RasterColorizer(
            mapnik.COLORIZER_LINEAR,
            mapnik.Color('white')
        )
        # colorizer.epsilon = 0.001

        for stop in self.colormap:
            colorizer.add_stop(stop['quantity'], mapnik.Color(
                stop['color'].encode('ascii')))


        sym.colorizer = colorizer
        rule.symbols.append(sym)
        style.rules.append(rule)

        Map.append_style('Raster Style', style)

        lyr = mapnik.Layer('GDAL Layer from TIFF', self.layer_srs)

        lyr.datasource = mapnik.Gdal(base=os.path.dirname(self.vrt_path),
                                     file=os.path.basename(self.vrt_path),\
                                     band=self.band)

        lyr.styles.append('Raster Style')

        Map.layers.append(lyr)

        return Map

    def renderArea(self, width, height, srs, xmin, ymin, xmax, ymax, zoom):
        '''
        '''

        # NB: To be thread-safe Map object cannot be stored as apart
        #     of the class, see: https://groups.google.com/forum/#!topic/mapnik/USDlVfSk328

        Map = mapnik.Map(width, height, srs)
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
