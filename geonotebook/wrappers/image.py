import gdal
import rasterio as rio
from collections import namedtuple

BBox = namedtuple('BBox', ['ulx', 'uly', 'lrx', 'lry'])

class BandStats(object):
    MIN = u'STATISTICS_MINIMUM'
    MAX = u'STATISTICS_MAXIMUM'
    MEAN = u'STATISTICS_MEAN'
    STDDEV = u'STATISTICS_STDDEV'


class GeoTiffImage(object):
    def __init__(self, path, band_names=None):
        self.path = path
        self.band_names = []
        self.dataset = rio.open(path)

    def __del__(self):
        self.dataset.close()

    def index(self, *args, **kwargs):
        return self.dataset.index(*args, **kwargs)

    def read(self, *args, **kwargs):
        return self.dataset.read(*args, **kwargs)

    # Dataset level API
    @property
    def count(self):
        return self.dataset.count

    @property
    def height(self):
        return self.dataset.height

    @property
    def width(self):
        return self.dataset.width

    @property
    def bounds(self):
        return BBox(self.dataset.bounds.left,
                    self.dataset.bounds.top,
                    self.dataset.bounds.right,
                    self.dataset.bounds.bottom)

    def _get_band_tag(self, index, prop, convert=float):
        assert not index < 0, \
            IndexError("Bands are indexed from 1")

        assert not index > self.count, \
            IndexError("Band index out of range")

        return convert(self.dataset.tags(index)[prop])

    # Band level API
    def get_band_min(self, index):
        return self._get_band_tag(index, BandStats.MIN)

    def get_band_max(self, index):
        return self._get_band_tag(index, BandStats.MAX)

    def get_band_mean(self, index):
        return self._get_band_tag(index, BandStats.MEAN)

    def get_band_stddev(self, index):
        return self._get_band_tag(index, BandStats.STDDEV)

    def get_band_name(self, index, default=None):
        assert index > 0, \
            IndexError("Bands are indexed from 1")

        assert index <= self.count, \
            IndexError("Band index out of range")

        if default is None:
            default = "Band {}".format(index)

        try:
            return self.dataset.tags()['BAND_{}_NAME'.format(index)]
        except KeyError:
            return default

    def get_band_data(self, index, window=None):
        if window is None:
            return self.dataset.read(index)

        (ulx, uly), (lrx, lry) = window

        return self.dataset.read(index, window=((ulx, lrx), (uly, lry)))
