"""Export various objects representing shapes in geonotebook.

This module contains thin wrappers around shapely objects which provide
the ability to subset raster data objects via a ``subset`` member
function.
"""
from types import MethodType

import fiona
import numpy as np
from rasterio.features import geometry_mask
from shapely.geometry import asShape, geo


def mask_data(data, mask):
    """Generate a masked numpy array for multiple bands of data."""
    if data.shape[1:] == mask.shape:
        mask = mask.reshape((1,) + mask.shape)
        mask = np.repeat(mask, data.shape[0], axis=0)

    return np.ma.array(data, mask=mask)


def to_geojson(geom):
    """Convert a shapely object or geometry into geojson."""
    return geo.mapping(geom)


def to_feature(geom):
    """Convert a shapely object into a geojson feature."""
    geom = to_geojson(geom)
    return {
        'type': 'Feature',
        'geometry': geom,
        'properties': getattr(geom, 'properties', {})
    }


def feature_window(raster, feature):
    """Generate a window from the bounds of a geojson-like feature."""
    bounds = fiona.bounds(feature)
    return bounds_window(raster, bounds)


def bounds_window(raster, bounds):
    """Generate a window from the given bounds."""
    index1 = raster.index(bounds[0], bounds[3])
    index2 = raster.index(bounds[2], bounds[1])
    return ((index1[0], index2[0] + 1), (index1[1], index2[1] + 1))


def read_window(raster, window):
    """Read a masked window of the given raster."""
    return raster.read(window=window, boundless=True, masked=True)


def generate_mask(raster, polygons, window):
    """Generate a mask of the given polygons in a specific window."""
    transform = raster.transform * raster.transform.translation(
        window[0][0], window[1][0])
    shape = (window[0][1] - window[0][0]), (window[1][1] - window[1][0])
    return geometry_mask(polygons, shape, transform, all_touched=True)


def crop_point(point, raster, **kwargs):
    window = bounds_window(raster, point.bounds)
    return read_window(raster.reader, window), window


def subset_point(point, raster, **kwargs):
        data = point.crop(raster)[0]
        return data[0][0]


def crop_polygon(polygon, raster, **kwargs):
    window = bounds_window(raster.reader, polygon.bounds)
    return read_window(raster.reader, window), window


def subset_polygon(polygon, raster, **kwargs):
    data, window = polygon.crop(raster, **kwargs)
    geom = to_geojson(polygon)
    mask = generate_mask(raster.reader, [geom], window)
    return mask_data(data, mask)


def crop_mask(array, mask=None):
    """Crop a masked array to only rows and columns with valid data."""
    # http://stackoverflow.com/a/34731073
    if len(array.shape) == 2:
        array = array.reshape((1,) + array.shape)

    if mask is None:
        mask = array[0, ...].mask

    notmask = ~mask
    rows = np.flatnonzero(notmask.sum(axis=1))
    cols = np.flatnonzero(notmask.sum(axis=0))

    return array[..., rows.min(): rows.max() + 1, cols.min(): cols.max() + 1]


def wrap_shapely(shape):
    """Wrap a shapely geometry appending subsetting and masking methods."""
    gtype = shape.geom_type

    if gtype == 'Point':
        shape.crop = MethodType(crop_point, shape)
        shape.subset = MethodType(subset_point, shape)
    elif gtype == 'Polygon' or gtype == 'MultiPolygon':
        shape.crop = MethodType(crop_polygon, shape)
        shape.subset = MethodType(subset_polygon, shape)
    else:
        raise Exception('Unhandled geometry type "%s"' % gtype)

    return shape


def shape(obj, **props):
    """Generate a shape object from a geojson-like dictionary."""
    if obj.get('type') == 'Feature':
        props.update(obj.get('properties', {}))
        obj = obj['geometry']

    shape_object = asShape(obj)
    shape_object.properties = props
    return wrap_shapely(shape_object)
