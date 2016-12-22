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
        'uint8': 'Byte',
        'float32': 'Float32'
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

        self.nodata = kwargs.get('nodata', None)

        try:
            self.dtype = self.numpy_to_vrt_type[kwargs['dtype']]
        except KeyError:
            self.dtype = None

        # Note: The band value mapnik expects. If we are rendering
        #       an RGB and we have 3 _bands,  then we set bands to
        #       -1.  Mapnik will use the ColorInterp from the VRT
        #       to figure out the bands.  Otherwise the VRT will have
        #       a single VRTRasterBand so we set the band to 1
        self.band = -1 if len(self._bands) == 3 else 1

        self.opacity = kwargs.get('opacity', 1)
        self.gamma = kwargs.get('gamma', 1)

        self.colormap = kwargs.get('colormap', {})

        self.scale_factor = None


    def serialize(self):
        return {
            "filepath": self.filepath,
            "map_srs": self.map_srs,
            "vrt_path": self.vrt_path,
            "name": self.name,
            "opacity": self.opacity,
            "gamma": self.gamma,
            "nodata": self.nodata,
            "colormap": self.colormap,
            "is_static": True if self._static_vrt else False,
            "raster_x_size": self.raster_x_size,
            "raster_y_size": self.raster_y_size,
            "transform": self.transform,
            "nodata": self.nodata,
            "layer_srs": self.layer_srs
        }


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

        colors = ["Red", "Green", "Blue"]

        for i, b in enumerate(self._bands):
            vrt_band = VRTRasterBandType(dataType=self.dtype,
                                         band=i+1,
                                         NoDataValue=[str(self.nodata)])
            source = ComplexSourceType(
                NODATA=str(self.nodata),
                SourceFilename=[
                    SourceFilenameType(
                        relativeToVRT=0,
                        valueOf_=self.filepath)],
                SourceBand=[b])




            if len(self._bands) == 3:
                vrt_band.ColorInterp = [colors[i]]

                # Scale floats to 0-255 and set the band type to Byte
                #   Note: this ensures mapnik will use the nodata value
                #   for the alpha channel.
                if self.dtype == "Float32":
                    source.ScaleRatio = int(255)
                    vrt_band.dataType = 'Byte'

            vrt_band.ComplexSource.append(source)

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
        #from pudb.remote import set_trace; set_trace(term_size=(283, 87))

        style = mapnik.Style()
        rule = mapnik.Rule()

        sym = mapnik.RasterSymbolizer()
        sym.opacity = self.opacity

        colorizer = mapnik.RasterColorizer(
            mapnik.COLORIZER_DISCRETE,
            mapnik.Color('white')
        )
            # colorizer.epsilon = 0.001
        if self.colormap:
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

        def gamma_correct(im):
            """Fast gamma correction with PIL's image.point() method"""
            if self.gamma != 1.0:
                table = [pow(x/255., 1.0 / self.gamma) * 255 for x in range(256)]
                # Expand table to number of bands
                table = table * len(im.mode)
                return im.point(table)
            else:
                return im

        # b = BytesIO(img.tostring())
        img = Image.frombytes('RGBA', (width, height), img.tostring())

        img = gamma_correct(img)

        return img
