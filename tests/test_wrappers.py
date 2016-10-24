import pytest
import numpy as np
import shapely
from geonotebook.wrappers.image import validate_index
from geonotebook.wrappers import RasterData
from geonotebook.annotations import Rectangle

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


class MockReader(object):
    def __init__(self, path):
        self.path = path
        self.bands = np.copy(DATA[path])
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


def setup_module():
    RasterData.register("mock", MockReader)

def teardown_module():
    del RasterData._concrete_data_types["mock"]


def test_name():
    rd = RasterData("coords.mock")
    assert rd.name == "coords"

def test_bad_filetype():
    with pytest.raises(NotImplementedError):
        RasterData("foo.bar")

def test_count():
    rd = RasterData("coords.mock")
    assert rd.count == 5

    rd = RasterData("missing.mock")
    assert rd.count == 4

def test_length():
    rd = RasterData("coords.mock")
    assert len(rd) == 5

    rd = RasterData("missing.mock")
    assert len(rd) == 4

def test_min():
    rd = RasterData("coords.mock")
    assert rd.min == [1.0, 2.0, 3.0, 4.0, 5.0]

    rd = RasterData("missing.mock")
    assert rd.min == [1.0, 2.0, 3.0, 4.0]

    rd = RasterData("single.mock")
    assert rd.min == 1.0

def test_max():
    rd = RasterData("coords.mock")
    assert rd.max == [55.0, 56.0, 57.0, 58.0, 59.0]

    rd = RasterData("missing.mock")
    assert rd.max == [52.0, 52.0, 52.0, 52.0]

    rd = RasterData("single.mock")
    assert rd.max == 35.0


def test_subset():
    rd = RasterData("coords.mock")
    rect = Rectangle([(0,0), (2,0), (2,3), (0,3), (0,0)], None)
    assert (rd.subset(rect) == \
            np.array([[[  1.,   2.,   3.,   4.,   5.],
                       [ 21.,  21.,  21.,  21.,  21.]],
                      [[ 12.,  12.,  12.,  12.,  12.],
                       [ 22.,  22.,  22.,  22.,  22.]],
                      [[ 13.,  13.,  13.,  13.,  13.],
                       [ 23.,  23.,  23.,  23.,  23.]]])).all()


def test_mean():
    rd = RasterData("coords.mock")
    assert rd.mean == [32.6, 32.68, 32.76, 32.84, 32.92]

    rd = RasterData("missing.mock")
    assert rd.mean == [27.842105263157894,
                       27.894736842105264,
                       27.94736842105263,
                       28.0]

    rd = RasterData("single.mock")
    assert rd.mean == pytest.approx(22.3333333333)

def test_stddev():
    rd = RasterData("coords.mock")
    assert rd.stddev == [14.947909552843836,
                         14.925736162749226,
                         14.908467392726859,
                         14.896120300266107,
                         14.88870712990218]

    rd = RasterData("missing.mock")
    assert rd.stddev == [13.554036718164102,
                         13.451256004129974,
                         13.351418943754043,
                         13.254592054315205]

    rd = RasterData("single.mock")
    assert rd.stddev == 9.5335664307167285

def test_get_data_returns_masked_array():
    rd = RasterData("coords.mock")
    assert isinstance(rd.get_data(), np.ma.core.MaskedArray)

def test_get_data_masked_false_returns_ndarray():
    rd = RasterData("coords.mock")
    assert isinstance(rd.get_data(), np.ndarray)

def test_get_data_single_band():
    rd = RasterData("single.mock")

    assert (rd.get_data() == \
            np.array([[  1.,  21.,  31.],
                      [ 12.,  22.,  32.],
                      [ 13.,  23.,  33.],
                      [ 14.,  24.,  34.],
                      [ 15.,  25.,  35.]])).all()

def test_shape():
    rd = RasterData("coords.mock")
    assert hasattr(rd.shape, "exterior")
    assert hasattr(rd.shape.exterior, "coords")
    assert list(rd.shape.exterior.coords) == [(0.0, 0.0), (5.0, 0.0), (5.0, 5.0), (0.0, 5.0), (0.0, 0.0)]

def test_ix():
    rd = RasterData("coords.mock")
    assert rd.ix(0,0) == [ 1.0, 2.0, 3.0, 4.0, 5.0]

    rd = RasterData("single.mock")
    assert rd.ix(0,0) == 1.

def test_get_data_shape():
    rd = RasterData("rect.mock")
    assert rd.get_data().shape == (5, 3, 2)

    assert rd.get_data(axis=0).shape == (2, 5, 3)
    assert rd.get_data(axis=1).shape == (5, 2, 3)
    assert rd.get_data(axis=2).shape == (5, 3, 2)

def test_get_data_value():
    rd = RasterData("rect.mock")
    assert (rd.get_data() == \
         np.array([[[  1.,   2.],
                    [ 21.,  21.],
                    [ 31.,  31.]],
                   [[ 12.,  12.],
                    [ 22.,  22.],
                    [ 32.,  32.]],
                   [[ 13.,  13.],
                    [ 23.,  23.],
                    [ 33.,  33.]],
                   [[ 14.,  14.],
                    [ 24.,  24.],
                    [ 34.,  34.]],
                   [[ 15.,  15.],
                    [ 25.,  25.],
                    [ 35.,  35.]]])).all()


def test_window():
    rd = RasterData("rect.mock")
    assert \
        (rd.get_data(window=((1,1), (3,2))) == \
         np.array([[[ 22.,  22.],
                    [ 32.,  32.]]])).all()


    rd = RasterData("coords.mock")
    assert \
        (rd.get_data(window=((2,2), (5,4))) == \
         np.array([[[ 33.,  33.,  33.,  33.,  33.],
                    [ 43.,  43.,  43.,  43.,  43.],
                    [ 53.,  53.,  53.,  53.,  53.]],
                   [[ 34.,  34.,  34.,  34.,  34.],
                    [ 44.,  44.,  44.,  44.,  44.],
                    [ 54.,  54.,  54.,  54.,  54.]]])).all()


def test_nonmasked_array():
    rd = RasterData("missing.mock")
    assert (rd.get_data(masked=False) == \
            np.array([[[  1.00000000e+00,   2.00000000e+00,   3.00000000e+00,  4.00000000e+00],
                       [  2.10000000e+01,   2.10000000e+01,   2.10000000e+01, 2.10000000e+01],
                       [  3.10000000e+01,   3.10000000e+01,   3.10000000e+01, 3.10000000e+01],
                       [  4.10000000e+01,   4.10000000e+01,   4.10000000e+01, 4.10000000e+01],
                       [  5.10000000e+01,   5.10000000e+01,   5.10000000e+01, 5.10000000e+01]],
                      [[  1.20000000e+01,   1.20000000e+01,   1.20000000e+01, 1.20000000e+01],
                       [  2.20000000e+01,   2.20000000e+01,   2.20000000e+01, 2.20000000e+01],
                       [  3.20000000e+01,   3.20000000e+01,   3.20000000e+01, 3.20000000e+01],
                       [  4.20000000e+01,   4.20000000e+01,   4.20000000e+01, 4.20000000e+01],
                       [  5.20000000e+01,   5.20000000e+01,   5.20000000e+01, 5.20000000e+01]],
                      [[  1.30000000e+01,   1.30000000e+01,   1.30000000e+01, 1.30000000e+01],
                       [  2.30000000e+01,   2.30000000e+01,   2.30000000e+01, 2.30000000e+01],
                       [  3.30000000e+01,   3.30000000e+01,   3.30000000e+01, 3.30000000e+01],
                       [  4.30000000e+01,   4.30000000e+01,   4.30000000e+01, 4.30000000e+01],
                       [ -9.99900000e+03,  -9.99900000e+03,  -9.99900000e+03, -9.99900000e+03]],
                      [[  1.40000000e+01,   1.40000000e+01,   1.40000000e+01, 1.40000000e+01],
                       [  2.40000000e+01,   2.40000000e+01,   2.40000000e+01, 2.40000000e+01],
                       [  3.40000000e+01,   3.40000000e+01,   3.40000000e+01, 3.40000000e+01],
                       [ -9.99900000e+03,  -9.99900000e+03,  -9.99900000e+03, -9.99900000e+03],
                       [ -9.99900000e+03,  -9.99900000e+03,  -9.99900000e+03, -9.99900000e+03]],
                      [[  1.50000000e+01,   1.50000000e+01,   1.50000000e+01, 1.50000000e+01],
                       [  2.50000000e+01,   2.50000000e+01,   2.50000000e+01, 2.50000000e+01],
                       [ -9.99900000e+03,  -9.99900000e+03,  -9.99900000e+03, -9.99900000e+03],
                       [ -9.99900000e+03,  -9.99900000e+03,  -9.99900000e+03, -9.99900000e+03],
                       [ -9.99900000e+03,  -9.99900000e+03,  -9.99900000e+03, -9.99900000e+03]]])).all()




def test_masked_array():
    rd = RasterData("missing.mock")
    assert \
        (rd.get_data().mask == \
         np.array([[[False, False, False, False],
                    [False, False, False, False],
                    [False, False, False, False],
                    [False, False, False, False],
                    [False, False, False, False]],
                   [[False, False, False, False],
                    [False, False, False, False],
                    [False, False, False, False],
                    [False, False, False, False],
                    [False, False, False, False]],
                   [[False, False, False, False],
                    [False, False, False, False],
                    [False, False, False, False],
                    [False, False, False, False],
                    [ True,  True,  True,  True]],
                   [[False, False, False, False],
                    [False, False, False, False],
                    [False, False, False, False],
                    [ True,  True,  True,  True],
                    [ True,  True,  True,  True]],
                   [[False, False, False, False],
                    [False, False, False, False],
                    [ True,  True,  True,  True],
                    [ True,  True,  True,  True],
                    [ True,  True,  True,  True]]])).all()



def test_getitem_list_returns_raster_data():
    rd = RasterData("coords.mock")
    assert isinstance(rd[1,2,3], RasterData)
    assert len(rd[1,2,3]) == 3


def test_getitem_int_returns_raster_data():
    rd = RasterData("coords.mock")
    assert isinstance(rd[1], RasterData)
    assert len(rd[1]) == 1

def test_getitem_bad_throws_exception():
    rd = RasterData("coords.mock")
    with pytest.raises(AssertionError):
        rd[0]

    with pytest.raises(AssertionError):
        rd[[0, 1, 2]]

    with pytest.raises(IndexError):
        rd['foo']

    with pytest.raises(IndexError):
        rd[['foo', 'bar', 'baz']]


def test_raster_data_is_valid(tmpdir):
    p = tmpdir.mkdir("data").join("test.tif")
    p.write("BOGUS DATA")
    assert RasterData.is_valid(str(p))

def test_raster_data_is_not_valid_no_path(tmpdir):
    assert not RasterData.is_valid("/some/bogus/path.tif")

def test_raster_data_is_not_valid_no_class(tmpdir):
    p = tmpdir.mkdir("data").join("test.foo")
    p.write("BOGUS DATA")
    assert not RasterData.is_valid(str(p))
