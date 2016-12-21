from shapely.geometry import MultiPoint as sMultiPoint

from .base import Shape


class MultiPoint(sMultiPoint):
    def crop(self, raster_data, **kwargs):
        for geom in self.geoms:
            window = Shape.bounds_window(raster_data.reader, geom)
            yield Shape.read_window(raster_data, window), window
