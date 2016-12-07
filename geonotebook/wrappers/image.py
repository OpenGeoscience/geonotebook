from functools import wraps

import numpy as np
import rasterio as rio

from .bbox import BBox


class BandStats(object):
    MIN = u'STATISTICS_MINIMUM'
    MAX = u'STATISTICS_MAXIMUM'
    MEAN = u'STATISTICS_MEAN'
    STDDEV = u'STATISTICS_STDDEV'


def validate_index(func):
    @wraps(func)
    def _validate_index(self, index, *args, **kwargs):
        assert not index < 1, \
            IndexError("Bands are indexed from 1")

        assert not index > self.count, \
            IndexError("Band index out of range")

        return func(self, index, *args, **kwargs)
    return _validate_index


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
        return convert(self.dataset.tags(index)[prop])

    def get_band_ix(self, indexes, x, y):
        return list(self.dataset.sample([(x, y)], indexes=indexes))[0]

    # Band level API
    @validate_index
    def get_band_min(self, index, **kwargs):
        try:
            return self._get_band_tag(index, BandStats.MIN)
        except KeyError:
            return self.get_band_data(index, masked=True).min()

    @validate_index
    def get_band_max(self, index, **kwargs):
        try:
            return self._get_band_tag(index, BandStats.MAX)
        except KeyError:
            return self.get_band_data(index, masked=True).max()

    @validate_index
    def get_band_mean(self, index, **kwargs):
        try:
            return self._get_band_tag(index, BandStats.MEAN)
        except KeyError:
            return self.get_band_data(index, masked=True).mean()

    @validate_index
    def get_band_stddev(self, index, **kwargs):
        try:
            return self._get_band_tag(index, BandStats.STDDEV)
        except KeyError:
            return self.get_band_data(index, masked=True).std()

    @validate_index
    def get_band_nodata(self, index):
        return self.dataset.nodata

    @validate_index
    def get_band_name(self, index, default=None):
        if default is None:
            default = "Band {}".format(index)

        try:
            return self.dataset.tags()['BAND_{}_NAME'.format(index)]
        except KeyError:
            return default

    @validate_index
    def get_band_data(self, index, window=None, masked=True, **kwargs):

        def _get_band_data():
            if window is None:
                return self.dataset.read(index)

            (ulx, uly), (lrx, lry) = window

            return self.dataset.read(index, window=((ulx, lrx), (uly, lry)))

        if masked:
            return np.ma.masked_values(
                _get_band_data(), self.get_band_nodata(index)
            )
        else:
            return _get_band_data()
