import gdal
import rasterio as rio
from collections import namedtuple

BBox = namedtuple('BBox', ['ulx', 'uly', 'lrx', 'lry'])

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
