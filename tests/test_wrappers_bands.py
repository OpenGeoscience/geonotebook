import unittest
import numpy as np
from geonotebook.wrappers.image import validate_index
from geonotebook.wrappers import RasterData

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


def setUpModule():
    RasterData.register("mock", MockReader)

def tearDownModule():
    del RasterData._concrete_data_types["mock"]


class TestRasterData(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_count(self):
        rd = RasterData("coords.mock")
        self.assertEquals(rd.count, 5)

        rd = RasterData("missing.mock")
        self.assertEquals(rd.count, 4)

    def test_length(self):
        rd = RasterData("coords.mock")
        self.assertEquals(len(rd), 5)

        rd = RasterData("missing.mock")
        self.assertEquals(len(rd), 4)

    def test_min(self):
        rd = RasterData("coords.mock")
        self.assertEquals(rd.min, [1.0, 2.0, 3.0, 4.0, 5.0])

        rd = RasterData("missing.mock")
        self.assertEquals(rd.min, [1.0, 2.0, 3.0, 4.0])

    def test_max(self):
        rd = RasterData("coords.mock")
        self.assertEquals(rd.max, [55.0, 56.0, 57.0, 58.0, 59.0])

        rd = RasterData("missing.mock")
        self.assertEquals(rd.max, [52.0, 52.0, 52.0, 52.0])


    def test_mean(self):
        rd = RasterData("coords.mock")
        self.assertEquals(rd.mean, [32.6, 32.68, 32.76, 32.84, 32.92])

        rd = RasterData("missing.mock")
        self.assertEquals(rd.mean, [27.842105263157894,
                                    27.894736842105264,
                                    27.94736842105263,
                                    28.0])

    def test_stddev(self):
        rd = RasterData("coords.mock")
        self.assertEquals(rd.stddev, [14.947909552843836,
                                      14.925736162749226,
                                      14.908467392726859,
                                      14.896120300266107,
                                      14.88870712990218])

        rd = RasterData("missing.mock")
        self.assertEquals(rd.stddev, [13.554036718164102,
                                      13.451256004129974,
                                      13.351418943754043,
                                      13.254592054315205])

    def test_get_data_returns_masked_array(self):
        rd = RasterData("coords.mock")
        self.assertTrue(isinstance(rd.get_data(), np.ma.core.MaskedArray))

    def test_get_data_masked_false_returns_ndarray(self):
        rd = RasterData("coords.mock")
        self.assertTrue(isinstance(rd.get_data(), np.ndarray))

    def test_get_data_shape(self):
        rd = RasterData("rect.mock")
        self.assertEquals(rd.get_data().shape, (5, 3, 2))

        self.assertEquals(rd.get_data(axis=0).shape, (2, 5, 3))
        self.assertEquals(rd.get_data(axis=1).shape, (5, 2, 3))
        self.assertEquals(rd.get_data(axis=2).shape, (5, 3, 2))

    def test_get_data_value(self):
        rd = RasterData("rect.mock")
        self.assertTrue(
            (rd.get_data() == \
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
                        [ 35.,  35.]]])).all())


    def test_window(self):
        rd = RasterData("rect.mock")
        self.assertTrue(
            (rd.get_data(window=((1,1), (3,2))) == \
             np.array([[[ 22.,  22.],
                        [ 32.,  32.]]])).all())


        rd = RasterData("coords.mock")
        self.assertTrue(
            (rd.get_data(window=((2,2), (5,4))) == \
             np.array([[[ 33.,  33.,  33.,  33.,  33.],
                        [ 43.,  43.,  43.,  43.,  43.],
                        [ 53.,  53.,  53.,  53.,  53.]],
                       [[ 34.,  34.,  34.,  34.,  34.],
                        [ 44.,  44.,  44.,  44.,  44.],
                        [ 54.,  54.,  54.,  54.,  54.]]])).all())


    def test_masked_array(self):
        rd = RasterData("missing.mock")
        self.assertTrue(
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
                        [ True,  True,  True,  True]]])).all())

    def test_getitem_single_index_band_class(self):
        rd = RasterData("coords.mock")
        self.assertTrue(isinstance(rd[0], RasterData.band_class))


    def test_getitem_slice_returns_raster_data(self):
        rd = RasterData("coords.mock")
        self.assertTrue(isinstance(rd[1:3], RasterData))
        self.assertEquals(len(rd[1:3]), 2)

    def test_getitem_list_returns_raster_data(self):
        rd = RasterData("coords.mock")
        self.assertTrue(isinstance(rd[[1,2,3]], RasterData))
        self.assertEquals(len(rd[1,2,3]), 3)

    def test_getitem_tuple_returns_raster_data(self):
        rd = RasterData("coords.mock")
        self.assertTrue(isinstance(rd[[1,2,3]], RasterData))
        self.assertEquals(len(rd[1,2,3]), 3)
