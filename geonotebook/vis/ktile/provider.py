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

global_mapnik_lock = allocate_lock()


DEFAULT_MAP_SRS = '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 ' + \
    '+lon_0=0.0 +x_0=0.0 +y_0=0.0 +k=1.0 +units=m ' +\
    '+nadgrids=@null +wktext +no_defs +over'


class MapnikPythonProvider(object):
    def __init__(self, layer, **kwargs):
        # List of bands to display,  should be len == 1 or len == 3
        self._bands = kwargs.get('bands', -1)
        self._last_hash = None

        self._vrt_path = os.path.join(
            tempfile.mkdtemp(), '{}.vrt'.format(kwargs.get('name', 'no_name')))

        self._filepath = None


        self.layer = layer

        self.filepath = kwargs.pop('path', None)
        self.map_srs = kwargs.pop('map_srs', DEFAULT_MAP_SRS)

        self.name = kwargs.get('name', None)


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
            tuple(tuple(cm.items()) for cm in self.colormap),
            self.scale_factor))


    def _generate_vrt(self):
        # Hard coded hack for now
        vrt = parseString('''
<VRTDataset rasterXSize='7243' rasterYSize='1900'>
  <SRS>GEOGCS['WGS 84',DATUM['WGS_1984',SPHEROID['WGS 84',6378137,298.257223563,AUTHORITY['EPSG','7030']],AUTHORITY['EPSG','6326']],PRIMEM['Greenwich',0,AUTHORITY['EPSG','8901']],UNIT['degree',0.0174532925199433,AUTHORITY['EPSG','9122']],AUTHORITY['EPSG','4326']]</SRS>
  <GeoTransform> -1.2306229313641593e+02,  7.5176108435883674e-04,  0.0000000000000000e+00,  4.8571429239198785e+01,  0.0000000000000000e+00, -7.5176108435883674e-04</GeoTransform>
  <VRTRasterBand dataType='Float32' band='1'>
    <NoDataValue>-9999</NoDataValue>
    <ColorInterp>Gray</ColorInterp>
    <ComplexSource>
      <SourceFilename relativeToVRT='1'>{}</SourceFilename>
      <SourceBand>1</SourceBand>
      <SourceProperties RasterXSize='7243' RasterYSize='1900' DataType='Float32' BlockXSize='7243' BlockYSize='1' />
      <SrcRect xOff='0' yOff='0' xSize='7243' ySize='1900' />
      <DstRect xOff='0' yOff='0' xSize='7243' ySize='1900' />
      <NODATA>-9999</NODATA>
    </ComplexSource>
  </VRTRasterBand>
</VRTDataset>
        '''.format(self.filepath), silence=True)

        with open(self._vrt_path, 'w') as fh:
            vrt.export(fh, 0)



    @property
    def vrt_path(self):
        if self._last_hash != hash(self):
            self._generate_vrt()
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
            raster = gdal.Open(self.filepath)
            srs = osr.SpatialReference()
            srs.ImportFromWkt(raster.GetProjectionRef())
            self._layer_srs = srs.ExportToProj4()

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
            mapnik.COLORIZER_DISCRETE,
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
