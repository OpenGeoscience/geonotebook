import matplotlib as mpl  # noqa
mpl.use('Agg')  # noqa

from contextlib import contextmanager
import os

import numpy as np
import pytest
from rasterio.crs import CRS

from geonotebook import layers
from geonotebook.wrappers import RasterData, RasterDataCollection
from geonotebook.wrappers.file_reader import validate_index

from .conftest_data import DATA


class MockReader(object):
    def __init__(self, uri):
        self.uri = uri
        self.bands = DATA[uri]
        self.nodata = -9999.0

    def index(self, *args):
        return args

    @property
    def count(self):
        return len(self.bands)

    @property
    def height(self):
        return self.bands.shape[2]

    @property
    def width(self):
        return self.bands.shape[1]

    @property
    def bounds(self):
        lat, lon = self.bands[0].shape
        return (0, 0, lat, lon)

    @property
    def crs(self):
        return CRS.from_string("EPSG:4326")

    def get_band_ix(self, indexes, x, y):
        return list(self.get_band_data(i)[y, x]
                    for i in indexes)

    @validate_index
    def get_band_min(self, index, **kwargs):
        return self.get_band_data(index, **kwargs).min()

    @validate_index
    def get_band_max(self, index, **kwargs):
        return self.get_band_data(index, **kwargs).max()

    @validate_index
    def get_band_mean(self, index, **kwargs):
        return self.get_band_data(index, **kwargs).mean()

    @validate_index
    def get_band_stddev(self, index, **kwargs):
        return self.get_band_data(index, **kwargs).std()

    @validate_index
    def get_band_nodata(self, index):
        return self.nodata

    @validate_index
    def get_band_name(self, index, default=None):
        return u"Band {}".format(index)

    @validate_index
    def get_band_data(self, index, window=None, masked=True, **kwargs):
        def _get_band_data():
            if window is None:
                return self.bands[index - 1]

            (ulx, uly), (lrx, lry) = window

            return self.bands[index - 1][uly:lry, ulx:lrx]

        if masked:
            return np.ma.masked_values(
                _get_band_data(),
                self.get_band_nodata(index)
            )
        else:
            return _get_band_data()


# Provide an easy way to register "mock" as a concreate data type
# This is intended for a few tests that that need to directly instantiate
# a RasterData or RasterDataCollection object in order to test object
# creation. Unfortunately we can't use this context manager inside the
# fixtures because of pytest magic.  See:
# http://stackoverflow.com/questions/15801662/py-test-how-to-use-a-context-manager-in-a-funcarg-fixture
@contextmanager
def enable_mock():
    RasterData.register("mock", MockReader)
    RasterData._default_schema = 'mock'

    yield

    if "mock" in RasterData._concrete_schema:
        del RasterData._concrete_schema["mock"]
    RasterData._default_schema = 'file'


@pytest.fixture
def coords():
    RasterData.register("mock", MockReader)
    RasterData._default_schema = 'mock'

    yield RasterData("coords.mock")

    if "mock" in RasterData._concrete_schema:
        del RasterData._concrete_schema["mock"]
    RasterData._default_schema = 'file'


@pytest.fixture
def missing():
    RasterData.register("mock", MockReader)
    RasterData._default_schema = 'mock'

    yield RasterData("missing.mock")

    if "mock" in RasterData._concrete_schema:
        del RasterData._concrete_schema["mock"]
    RasterData._default_schema = 'file'


@pytest.fixture
def single():
    RasterData.register("mock", MockReader)
    RasterData._default_schema = 'mock'

    yield RasterData("single.mock")

    if "mock" in RasterData._concrete_schema:
        del RasterData._concrete_schema["mock"]
    RasterData._default_schema = 'file'


@pytest.fixture
def rect():
    RasterData.register("mock", MockReader)
    RasterData._default_schema = 'mock'

    yield RasterData("rect.mock")

    if "mock" in RasterData._concrete_schema:
        del RasterData._concrete_schema["mock"]
    RasterData._default_schema = 'file'


# TimeSeriesLayer
class RDMock(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def rasterdata_list():
    RasterData.register("mock", MockReader)
    RasterData._default_schema = 'mock'
    yield RasterDataCollection(['test_data1.tif',
                                'test_data2.tif',
                                'test_data3.tif'])

    if "mock" in RasterData._concrete_schema:
        del RasterData._concrete_schema["mock"]
    RasterData._default_schema = 'file'


# RasterDataCollection
@pytest.fixture
def rdc_rect():
    RasterData.register("mock", MockReader)
    RasterData._default_schema = 'mock'

    yield RasterDataCollection([
        "rect1.mock", "rect2.mock", "rect3.mock"])

    if "mock" in RasterData._concrete_schema:
        del RasterData._concrete_schema["mock"]
    RasterData._default_schema = 'file'


@pytest.fixture
def rdc_single():
    RasterData.register("mock", MockReader)
    RasterData._default_schema = 'mock'

    yield RasterDataCollection([
        "single1.mock", "single2.mock", "single3.mock"])

    if "mock" in RasterData._concrete_schema:
        del RasterData._concrete_schema["mock"]
    RasterData._default_schema = 'file'


@pytest.fixture
def rdc_one():
    RasterData.register("mock", MockReader)
    RasterData._default_schema = 'mock'

    yield RasterDataCollection(["rect1.mock"])

    if "mock" in RasterData._concrete_schema:
        del RasterData._concrete_schema["mock"]
    RasterData._default_schema = 'file'


# Geonotebook Layer fixtures
@pytest.fixture
def glc():
    # glc: Geonotebook Layer Collection

    foo = layers.GeonotebookLayer('foo', None, None, vis_url='vis')
    bar = layers.GeonotebookLayer('bar', None, None, vis_url='vis')
    baz = layers.GeonotebookLayer('baz', None, None, vis_url='vis')

    return layers.GeonotebookLayerCollection([foo, bar, baz])


@pytest.fixture
def glc_annotation(rect, coords, single, missing):
    glc = layers.GeonotebookLayerCollection([
        layers.DataLayer('rect', None, rect, vis_url='vis'),
        layers.DataLayer('coords', None, coords, vis_url='vis'),
        layers.DataLayer('single', None, single, vis_url='vis'),
        layers.DataLayer('missing', None, missing, vis_url='vis')])

    glc.append(layers.AnnotationLayer(
        'annotation', None, glc, expose_as="annotation", system_layer=True))

    return glc


@pytest.fixture
def geonotebook_layer():
    return layers.GeonotebookLayer('foo', None, None, vis_url='vis')


# Vis Server fixtures

DEFAULT_GEONOTEBOOK_INI_CONFIG = """
[default]
vis_server = geoserver

[geoserver]
username = admin
password = geoserver
url = http://0.0.0.0:8080/geoserver
"""


@pytest.fixture
def geonotebook_ini(tmpdir):
    p = tmpdir.mkdir('config').join("geonotebook.ini")
    p.write(DEFAULT_GEONOTEBOOK_INI_CONFIG)
    os.environ["GEONOTEBOOK_INI"] = str(p)


@pytest.fixture
def visserver(mocker, monkeypatch):
    import geonotebook
    visserver = mocker.patch('geonotebook.vis.geoserver.geoserver.Geoserver')
    monkeypatch.setitem(
        geonotebook.config.Config._valid_vis_hash,
        'geoserver', visserver
    )
    return visserver.return_value


# Annotation fixtures
@pytest.fixture
def point_coords():
    return [-73.82630311108075, 42.74910719142488]


@pytest.fixture
def rect_coords():
    return [
        [-75.07115526394361, 42.497950296616835],
        [-75.07115526394361, 42.716333796366044],
        [-74.70974657440277, 42.716333796366044],
        [-74.70974657440277, 42.497950296616835],
        [-75.07115526394361, 42.497950296616835]]


@pytest.fixture
def poly_coords():
    return [
        [-74.36395430971865, 43.19961074294126],
        [-74.51342580477566, 43.09869810847833],
        [-74.35056880269862, 42.92905123923207],
        [-74.12970793686812, 42.93721806175041],
        [-74.02708571638122, 43.06936968778549],
        [-74.19663547196826, 43.19961074294126],
        [-74.36395430971865, 43.19961074294126]]
