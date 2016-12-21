import fiona
import numpy as np
from rasterio.features import geometry_mask
from shapely.geometry import geo


class Shape(object):
    """A class mixin defining various convenience methods for shape objects.

    Shapes are vector-like objects that act on raster-like objects to
    perform operations such as subsetting, masking, and querying. They
    exist to support Annotation and Vector objects inside geonotebook.
    These mixins define common operations for acting on numpy, rasterio,
    and fiona datastructures.
    """

    @classmethod
    def mask_data(cls, data, mask):
        """Generate a masked numpy array for multiple bands of data."""
        if data.shape[1:] == mask.shape:
            mask = mask.reshape((1,) + mask.shape)
            mask = np.repeat(mask, data.shape[0], axis=0)

        return np.ma.array(data, mask=mask)

    @classmethod
    def to_geojson(cls, geom):
        """Convert a shapely object or geometry into geojson."""
        return geo.mapping(geom)

    @classmethod
    def to_feature(cls, geom):
        """Convert a shapely object into a geojson feature."""
        geom = cls.to_geojson(geom)
        return {
            'type': 'Feature',
            'geometry': geom,
            'properties': {}
        }

    @classmethod
    def feature_window(cls, raster, feature):
        """Generate a window from the bounds of a geojson-like feature."""
        bounds = fiona.bounds(feature)
        return cls.bounds_window(raster, bounds)

    @classmethod
    def bounds_window(cls, raster, bounds):
        """Generate a window from the given bounds."""
        index1 = raster.index(*bounds[:2])
        index2 = raster.index(*bounds[2:])
        return ((index1[0], index2[0] + 1), (index1[1], index2[1] + 1))

    @classmethod
    def read_window(cls, raster, window):
        """Read a masked window of the given raster."""
        return raster.read(window=window, boundless=True, masked=True)

    @classmethod
    def generate_mask(cls, raster, polygons, window):
        """Generate a mask of the given polygons in a specific window."""
        transform = raster.transform * raster.transform.translation(
            window[0][0], window[1][0])
        shape = (window[0][1] - window[0][0]), (window[1][1] - window[1][0])
        return geometry_mask(polygons, shape, transform, all_touched=True)
