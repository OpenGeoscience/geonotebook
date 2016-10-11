from shapely.geometry import Point as sPoint
from shapely.geometry import Polygon as sPolygon
from rasterio.features import rasterize
from wrappers import RasterData, RasterDataCollection
import numpy as np


class Annotation(object):
    def __init__(self, *args, **kwargs):
        self.layer = kwargs.pop('layer', None)

        self._metadata = kwargs
        for k, v in kwargs.items():
            setattr(Annotation, k, property(self._get_metadata(k),
                                            self._set_metadata(k),
                                            None))

        super(Annotation, self).__init__(*args)


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
    def __init__(self, x, y, **kwargs):
        super(Point, self).__init__(x, y, **kwargs)

    def subset(self, raster_data, **kwargs):
        return raster_data.ix(self.x, self.y)


class Rectangle(Annotation, sPolygon):
    def __init__(self, coordinates, holes, **kwargs):
        super(Rectangle, self).__init__(coordinates, holes, **kwargs)

    def subset(self, raster_data, **kwargs):
        window = (raster_data.index(self.bounds[0], self.bounds[3]),
                  raster_data.index(self.bounds[2], self.bounds[1]))

        # TODO: Trim window to valid range for raster data if out of bounds

        return raster_data.get_data(window=window, **kwargs)


class Polygon(Annotation, sPolygon):
    def __init__(self, coordinates, holes, **kwargs):
        super(Polygon, self).__init__(coordinates, holes, **kwargs)

    def subset(self, raster_data, **kwargs):
        # It is possible our user has drawn a polygon where part of the
        # shape is outside the dataset,  intersect with the rasterdata
        # shape to make sure we don't try to select/mask data that is
        # outside the bounds of our dataset.
        clipped = self.intersection(raster_data.shape)

        # Polygon is completely outside the dataset, return whatever
        # would have been returned by get_data()
        if not bool(clipped):
            ul = raster_data.index(self.bounds[0], self.bounds[3])
            lr = raster_data.index(self.bounds[2], self.bounds[1])

            return raster_data.get_data(window=(ul, lr), **kwargs)


        ul = raster_data.index(clipped.bounds[0], clipped.bounds[3])
        lr = raster_data.index(clipped.bounds[2], clipped.bounds[1])

        data = raster_data.get_data(window=(ul, lr), **kwargs)

        # out_shape must be determined from data's shape,  get_data
        # may have returned a bounding box of data that is smaller than
        # the implicit shape of the window we passed.  e.g. if the window
        # is partially outside the extent of the raster data. Note that
        # we index with negative numbers here because we may or may not
        # have a time dimension.
        num_bands = len(raster_data.band_indexes)

        if num_bands > 1:
            out_shape = data.shape[-3], data.shape[-2]
        else:
            out_shape = data.shape[-2], data.shape[-1]



        coordinates = []
        for lat, lon in clipped.exterior.coords:
            x, y = raster_data.index(lat, lon)
            coordinates.append((y - ul[1], x - ul[0]))


        # Mask the final polygon
        mask = rasterize(
            [({'type': 'Polygon',
               'coordinates': [coordinates]}, 0)],
            out_shape=out_shape, fill=1, all_touched=True, dtype=np.uint8)

        # If we have more than one band,  expand the mask so it includes
        # A "channel" dimension (e.g.  shape is now (lat, lon, channel))
        if num_bands > 1:
            mask = mask[..., np.newaxis] * np.ones(num_bands)

        # Finally broadcast mask to data because data may be from a
        # Raster data collection and include a time component
        # (e.g.  shape could be (time, lat, lon),  or even
        #  (time, lat, lon, channels))
        _, mask = np.broadcast_arrays(data, mask)
        data[mask.astype(bool)] = raster_data.nodata

        return np.ma.masked_equal(data, raster_data.nodata)
