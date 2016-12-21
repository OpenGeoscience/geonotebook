from contextlib import contextmanager
import os
from tempfile import NamedTemporaryFile

from affine import Affine
import numpy as np
import rasterio
import shapely
import shapely.geometry

from geonotebook.shapes.base import Shape


@contextmanager
def rio_image(data, crs='+proj=latlong', transform=None):
    """Generate a rasterio image object from the given data."""
    fname = NamedTemporaryFile(suffix='.tif').name
    height, width = data.shape[-2:]
    count = data.shape[0]
    if len(data.shape) == 2:
        count = 1
        data = data.reshape((1,) + data.shape)
    if transform is None:
        transform = Affine.identity()
    raster = rasterio.open(
        fname, 'w',
        driver='GTiff',
        height=height, width=width,
        count=count,
        dtype=data.dtype,
        crs=crs, transform=transform
    )
    raster.write(data)
    yield raster
    try:
        os.remove(fname)
    except OSError:
        pass


def test_shape_mask_data_single():
    data = np.zeros((10, 7))
    mask = np.ones(data.shape, dtype=np.bool)
    masked = Shape.mask_data(data, mask)
    assert masked.mask is mask


def test_shape_mask_data_multi():
    data = np.zeros((5, 6, 3))
    mask = np.ones(data.shape[1:], dtype=np.bool)
    mask[1, 2] = False
    masked = Shape.mask_data(data, mask)
    for band in range(data.shape[0]):
        assert np.all(masked[band, ...].mask == mask)


def test_shape_to_geojson():
    point = shapely.geometry.Point(1, 2)
    geojson = Shape.to_geojson(point)
    assert geojson['type'] == 'Point'
    assert geojson['coordinates'] == (1.0, 2.0)


def test_shape_to_feature():
    polygon = shapely.geometry.Polygon(((0, 0), (1, 1), (0, 1), (0, 0)))
    geojson = Shape.to_feature(polygon)
    assert geojson['type'] == 'Feature'
    assert 'properties' in geojson
    assert geojson['geometry']['type'] == 'Polygon'
    assert geojson['geometry']['coordinates'] == \
        (tuple(polygon.exterior.coords),)


def test_shape_feature_window():
    data = np.zeros((25, 20))
    polygon = shapely.geometry.Polygon(
        ((5.5, 9.5), (10.5, 15.5), (5.5, 15.5), (5.5, 9.5))
    )
    feature = Shape.to_feature(polygon)
    with rio_image(data) as raster:
        window = Shape.feature_window(raster, feature)
        assert window == ((9, 16), (5, 11))


def test_shape_bounds_window():
    data = np.zeros((25, 20))
    bounds = (5.5, 7.5, 11.5, 12.5)
    with rio_image(data) as raster:
        window = Shape.bounds_window(raster, bounds)
        assert window == ((7, 13), (5, 12))


def test_read_window():
    data = np.arange(3 * 7 * 5, dtype=np.float64).reshape(3, 7, 5)
    window = ((2, 4), (1, 4))
    with rio_image(data) as raster:
        subset = Shape.read_window(raster, window)
        assert np.all(subset == data[:, 2:4, 1:4])


def test_generate_mask():
    data = np.arange(3 * 7 * 5, dtype=np.float64).reshape(3, 7, 5)
    polygon = Shape.to_geojson(shapely.geometry.Polygon(
        ((1.5, 2.5), (3.5, 2.5), (3.5, 5.5), (1.5, 5.5), (1.5, 2.5))
    ))
    window = ((0, data.shape[1]), (0, data.shape[2]))
    with rio_image(data) as raster:
        mask = Shape.generate_mask(raster, [polygon], window)
        assert mask.shape == data.shape[1:]
        assert np.all(mask[2:6, 1:4] == False)  # noqa: E712
        mask[2:6, 1:4] = True
        assert np.all(mask)
