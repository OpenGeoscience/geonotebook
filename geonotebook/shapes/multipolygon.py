from shapely.geometry import MultiPolygon as sMultiPolygon

from .base import Shape


class MultiPolygon(sMultiPolygon):
    def crop(self, raster_data, **kwargs):
        window = Shape.bounds_window(raster_data, self.bounds)
        return Shape.read_window(raster_data, window), window

    def subset(self, raster_data, **kwargs):
        data, window = self.crop(raster_data, **kwargs)
        geom = Shape.to_geojson(self)
        mask = Shape.generate_mask(raster_data, [geom], window)
        return Shape.mask_data(data, mask)
