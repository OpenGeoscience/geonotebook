from shapely.geometry import Point as sPoint
from shapely.geometry import Polygon as sPolygon
from rasterio.features import rasterize
import numpy as np


class Annotation(object):
    def __init__(self, layer, coordinates, **kwargs):
        super(Annotation, self).__init__()

        self.layer = layer
        self._coordinates = coordinates
        self._metadata = kwargs
        for k, v in kwargs.items():
            setattr(Annotation, k, property(self._get_metadata(k),
                                            self._set_metadata(k),
                                            None))

    def _get_metadata(self, k):
        def __get_metadata(self):
            return self._metadata[k]
        return __get_metadata

    def _set_metadata(self, k):
        def __set_metadata(self, v):
            # TODO: these will have to communicate
            # updates to the clientside via self.layer._remote
            self._metadata[k] = v
        return __set_metadata

    @property
    def data(self):
        for layer in self.layer.stack:
            if hasattr(layer, "data") and layer.data is not None:
                yield layer, self.subset(layer.data, **self._metadata)

class Point(Annotation, sPoint):
    def __init__(self, layer, coordinates, **kwargs):
        super(Point, self).__init__(layer, coordinates, **kwargs)
        sPoint.__init__(self, coordinates[0]['x'], coordinates[0]['y'])

    def subset(self, raster_data, **kwargs):
        return raster_data.ix(self.x, self.y)

class Rectangle(Annotation, sPolygon):
    def __init__(self, layer, coordinates, **kwargs):
        super(Rectangle, self).__init__(layer, coordinates, **kwargs)
        sPolygon.__init__(self, [(c['x'], c['y']) for c in coordinates])

    def subset(self, raster_data, **kwargs):
        window = (raster_data.index(self.bounds[0], self.bounds[3]),
                  raster_data.index(self.bounds[2], self.bounds[1]))

        # TODO: Trim window to valid range for this rasterdata set

        return raster_data.get_data(window=window, **kwargs)


class Polygon(Annotation, sPolygon):
    def __init__(self, layer, coordinates, **kwargs):
        super(Polygon, self).__init__(layer, coordinates, **kwargs)
        sPolygon.__init__(self, [(c['x'], c['y']) for c in coordinates])

    def subset(self, raster_data, **kwargs):

        ul = raster_data.index(self.bounds[0], self.bounds[3])
        lr = raster_data.index(self.bounds[2], self.bounds[1])

        data = raster_data.get_data(window=(ul, lr), **kwargs)

        coordinates = []
        for lat, lon in self.exterior.coords:
            x, y = raster_data.index(lat, lon)
            coordinates.append((y - ul[1], x - ul[0]))

        out_shape = (abs(ul[0] - lr[0]), abs(ul[1] - lr[1]))

        mask = rasterize(
            [({'type': 'Polygon',
               'coordinates': [coordinates]}, 0)],
            out_shape=out_shape, fill=1, all_touched=True, dtype=np.uint8)

        if len(data.shape) > 2:
            mask = (mask[:,:,np.newaxis] * ([1] * data.shape[2])).astype(bool)
        else:
            mask = np.ma.array(data, mask=mask.astype(bool))

        data[mask] = raster_data.nodata

        return data
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
