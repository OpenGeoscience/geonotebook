import matplotlib as mpl
mpl.use('Agg')

import os
import pytest
import numpy as np
from geonotebook import layers
from contextlib import contextmanager
from geonotebook.wrappers.image import validate_index
from geonotebook.wrappers import RasterData, RasterDataCollection

# RasterData fixtures and test code

DATA = {"coords.mock": np.array([ [[ 1.0, 21.0, 31.0, 41.0, 51.0],
                                   [12.0, 22.0, 32.0, 42.0, 52.0],
                                   [13.0, 23.0, 33.0, 43.0, 53.0],
                                   [14.0, 24.0, 34.0, 44.0, 54.0],
                                   [15.0, 25.0, 35.0, 45.0, 55.0]],
                                  [[ 2.0, 21.0, 31.0, 41.0, 51.0],
                                   [12.0, 22.0, 32.0, 42.0, 52.0],
                                   [13.0, 23.0, 33.0, 43.0, 53.0],
                                   [14.0, 24.0, 34.0, 44.0, 54.0],
                                   [15.0, 25.0, 35.0, 45.0, 56.0]],
                                  [[ 3.0, 21.0, 31.0, 41.0, 51.0],
                                   [12.0, 22.0, 32.0, 42.0, 52.0],
                                   [13.0, 23.0, 33.0, 43.0, 53.0],
                                   [14.0, 24.0, 34.0, 44.0, 54.0],
                                   [15.0, 25.0, 35.0, 45.0, 57.0]],
                                  [[ 4.0, 21.0, 31.0, 41.0, 51.0],
                                   [12.0, 22.0, 32.0, 42.0, 52.0],
                                   [13.0, 23.0, 33.0, 43.0, 53.0],
                                   [14.0, 24.0, 34.0, 44.0, 54.0],
                                   [15.0, 25.0, 35.0, 45.0, 58.0]],
                                  [[ 5.0, 21.0, 31.0, 41.0, 51.0],
                                   [12.0, 22.0, 32.0, 42.0, 52.0],
                                   [13.0, 23.0, 33.0, 43.0, 53.0],
                                   [14.0, 24.0, 34.0, 44.0, 54.0],
                                   [15.0, 25.0, 35.0, 45.0, 59.0]]]),
        "missing.mock": np.array([ [[ 1.0,    21.0,    31.0,    41.0,    51.0],
                                    [12.0,    22.0,    32.0,    42.0,    52.0],
                                    [13.0,    23.0,    33.0,    43.0, -9999.0],
                                    [14.0,    24.0,    34.0, -9999.0, -9999.0],
                                    [15.0,    25.0, -9999.0, -9999.0, -9999.0]],
                                   [[ 2.0,    21.0,    31.0,    41.0,    51.0],
                                    [12.0,    22.0,    32.0,    42.0,    52.0],
                                    [13.0,    23.0,    33.0,    43.0, -9999.0],
                                    [14.0,    24.0,    34.0, -9999.0, -9999.0],
                                    [15.0,    25.0, -9999.0, -9999.0, -9999.0]],
                                   [[ 3.0,    21.0,    31.0,      41,      51],
                                    [12.0,    22.0,    32.0,      42,      52],
                                    [13.0,    23.0,    33.0,      43, -9999.0],
                                    [14.0,    24.0,    34.0, -9999.0, -9999.0],
                                    [15.0,    25.0, -9999.0, -9999.0, -9999.0]],
                                   [[ 4.0,    21.0,    31.0,    41.0,    51.0],
                                    [12.0,    22.0,    32.0,    42.0,    52.0],
                                    [13.0,    23.0,    33.0,    43.0, -9999.0],
                                    [14.0,    24.0,    34.0, -9999.0, -9999.0],
                                    [15.0,    25.0, -9999.0, -9999.0, -9999.0]]]),
        "rect.mock": np.array([ [[ 1.0, 21.0, 31.0],
                                 [12.0, 22.0, 32.0],
                                 [13.0, 23.0, 33.0],
                                 [14.0, 24.0, 34.0],
                                 [15.0, 25.0, 35.0]],
                                [[ 2.0, 21.0, 31.0],
                                 [12.0, 22.0, 32.0],
                                 [13.0, 23.0, 33.0],
                                 [14.0, 24.0, 34.0],
                                 [15.0, 25.0, 35.0]]]),
        "single.mock" : np.array([ [[ 1.0, 21.0, 31.0],
                                    [12.0, 22.0, 32.0],
                                    [13.0, 23.0, 33.0],
                                    [14.0, 24.0, 34.0],
                                    [15.0, 25.0, 35.0]]])

}

# Setup mock data for rasterdata collection tests
DATA['rect1.mock'] = np.copy(DATA['rect.mock'])
DATA['rect1.mock'][0][0][0] = 100.
DATA['rect2.mock'] = np.copy(DATA['rect.mock'])
DATA['rect2.mock'][0][0][0] = 200.
DATA['rect3.mock'] = np.copy(DATA['rect.mock'])
DATA['rect3.mock'][0][0][0] = 300.

DATA['single1.mock'] = np.copy(DATA['single.mock'])
DATA['single1.mock'][0][0] = 100.
DATA['single2.mock'] = np.copy(DATA['single.mock'])
DATA['single2.mock'][0][0] = 200.
DATA['single3.mock'] = np.copy(DATA['single.mock'])
DATA['single3.mock'][0][0] = 300.


class MockReader(object):
    def __init__(self, path):
        self.path = path
        self.bands = DATA[path]
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

    def get_band_ix(self, indexes, x, y):
        return list(self.get_band_data(i)[y,x]
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
                return self.bands[index-1]

            (ulx, uly), (lrx, lry) = window

            return self.bands[index-1][uly:lry,ulx:lrx]

        if masked:
            return np.ma.masked_values(_get_band_data(), self.get_band_nodata(index))
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

    yield

    if "mock" in RasterData._concrete_data_types:
        del RasterData._concrete_data_types["mock"]



@pytest.fixture
def coords():
    RasterData.register("mock", MockReader)

    yield RasterData("coords.mock")

    if "mock" in RasterData._concrete_data_types:
        del RasterData._concrete_data_types["mock"]

@pytest.fixture
def missing():
    RasterData.register("mock", MockReader)

    yield RasterData("missing.mock")

    if "mock" in RasterData._concrete_data_types:
        del RasterData._concrete_data_types["mock"]

@pytest.fixture
def single():
    RasterData.register("mock", MockReader)

    yield RasterData("single.mock")

    if "mock" in RasterData._concrete_data_types:
        del RasterData._concrete_data_types["mock"]

@pytest.fixture
def rect():
    RasterData.register("mock", MockReader)

    yield RasterData("rect.mock")

    if "mock" in RasterData._concrete_data_types:
        del RasterData._concrete_data_types["mock"]


# TimeSeriesLayer
class RDMock(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

@pytest.fixture
def rasterdata_list():
    return [RDMock(name='test_data1.tif'),
            RDMock(name='test_data2.tif'),
            RDMock(name='test_data3.tif')]



# RasterDataCollection
@pytest.fixture
def rdc_rect():
    RasterData.register("mock", MockReader)

    yield RasterDataCollection([
        "rect1.mock", "rect2.mock", "rect3.mock"])

    if "mock" in RasterData._concrete_data_types:
        del RasterData._concrete_data_types["mock"]


@pytest.fixture
def rdc_single():
    RasterData.register("mock", MockReader)

    yield RasterDataCollection([
        "single1.mock", "single2.mock", "single3.mock"])

    if "mock" in RasterData._concrete_data_types:
        del RasterData._concrete_data_types["mock"]


@pytest.fixture
def rdc_one():
    RasterData.register("mock", MockReader)

    yield RasterDataCollection(["rect1.mock"])

    if "mock" in RasterData._concrete_data_types:
        del RasterData._concrete_data_types["mock"]




# Geonotebook Layer fixtures
@pytest.fixture
def glc():
    """ glc: Geonotebook Layer Collection """

    foo = layers.GeonotebookLayer('foo', None, vis_url='vis')
    bar = layers.GeonotebookLayer('bar', None, vis_url='vis')
    baz = layers.GeonotebookLayer('baz', None, vis_url='vis')

    return layers.GeonotebookLayerCollection([foo, bar, baz])


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
    monkeypatch.setitem(geonotebook.config.Config._valid_vis_hash, 'geoserver', visserver)
    return visserver.return_value



# Annotation fixtures

@pytest.fixture
def point_coords():
    return [{'x': -73.82630311108075, 'y': 42.74910719142488}]

@pytest.fixture
def rect_coords():
    return [
        {'x': -75.07115526394361, 'y': 42.497950296616835},
        {'x': -75.07115526394361, 'y': 42.716333796366044},
        {'x': -74.70974657440277, 'y': 42.716333796366044},
        {'x': -74.70974657440277, 'y': 42.497950296616835},
        {'x': -75.07115526394361, 'y': 42.497950296616835}]

@pytest.fixture
def poly_coords():
    return [
        { 'x': -74.36395430971865, 'y': 43.19961074294126},
        { 'x': -74.51342580477566, 'y': 43.09869810847833},
        { 'x': -74.35056880269862, 'y': 42.92905123923207},
        { 'x': -74.12970793686812, 'y': 42.93721806175041},
        { 'x': -74.02708571638122, 'y': 43.06936968778549},
        { 'x': -74.19663547196826, 'y': 43.19961074294126},
        { 'x': -74.36395430971865, 'y': 43.19961074294126}]
