from shapely.geometry import Polygon as sPolygon

from .base import Shape


class Polygon(sPolygon):
    def crop(self, raster_data, **kwargs):
        window = Shape.bounds_window(raster_data.reader, self.bounds)
        return Shape.read_window(raster_data.reader, window), window

    def subset(self, raster_data, **kwargs):
        data, window = self.crop(raster_data, **kwargs)
        geom = Shape.to_geojson(self)
        mask = Shape.generate_mask(raster_data.reader, [geom], window)
        return Shape.mask_data(data, mask)
