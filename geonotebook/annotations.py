from shapely.geometry import Point as sPoint
from shapely.geometry import Polygon as sPolygon

class Point(sPoint):
    def __init__(self, coordinates, **kwargs):
        self._coordinates = coordinates
        for k, v in kwargs.items():
            setattr(self, k, v)

        super(Point, self).__init__(coordinates[0]['x'], coordinates[0]['y'])

    def subset(self, raster_data, **kwargs):
        return raster_data.ix(self.x, self.y)

class Rectangle(sPolygon):
    def __init__(self, coordinates, **kwargs):
        self._coordinates = coordinates
        for k, v in kwargs.items():
            setattr(self, k, v)

        super(Rectangle, self).__init__(
            [(c['x'], c['y']) for c in coordinates])

    def subset(self, raster_data, **kwargs):
        window = (raster_data.index(self.bounds[0], self.bounds[3]),
                  raster_data.index(self.bounds[2], self.bounds[1]))

        # TODO: Trim window to valid range for this rasterdata set

        return raster_data.get_data(window=window, **kwargs)


class Polygon(sPolygon):
    def __init__(self, coordinates, **kwargs):
        self._coordinates = coordinates
        for k, v in kwargs.items():
            setattr(self, k, v)

        super(Polygon, self).__init__(
            [(c['x'], c['y']) for c in coordinates])

    def subset(self, raster_data, **kwargs):
        raise NotImplemented("Subsetting with Polygons not implemented yet")


# Did not work.. some issue with rasterize & GDAL
#        import rasterio
#        from affine import Affine
#        from rasterio.features import rasterize
#        import numpy
#
#
#        ul = self.index(annotation.bounds[0], annotation.bounds[3])
#        lr = self.index(annotation.bounds[2], annotation.bounds[1])
#
#        window = ((lr[0], ul[0]+1), (ul[1], lr[1]+1))
#        data = self.get_data(window=window)
#
#        # create an affine transform for the subset data
#        t = self.reader.dataset.affine
#        shifted_affine = Affine(t.a, t.b, t.c+ul[1]*t.a, t.d, t.e, t.f+lr[0]*t.e)
#
#        # rasterize the geometry
#        mask = rasterize(
#            [(annotation, 0)],
#            out_shape=data.shape,
#            transform=shifted_affine,
#            fill=1,
#            all_touched=True,
#            dtype=numpy.uint8)
