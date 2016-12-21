from shapely.geometry import Polygon as sPolygon

from .base import Shape


class Rectangle(sPolygon):
    def crop(self, raster_data, **kwargs):
        window = Shape.bounds_window(raster_data, self.bounds)
        return Shape.read_window(raster_data, window), window

    def subset(self, raster_data, **kwargs):
        return self.crop(raster_data, **kwargs)[0]
