import pytest
import shapely
import numpy as np
from geonotebook.wrappers import RasterData
from geonotebook.annotations import Rectangle


def test_name(coords):
    assert coords.name == "coords"

def test_bad_filetype():
    with pytest.raises(NotImplementedError):
        RasterData("foo.bar")

def test_count(coords, missing):
    assert coords.count == 5
    assert missing.count == 4

def test_length(coords, missing):
    assert len(coords) == 5
    assert len(missing) == 4

def test_min(coords, missing, single):
    assert coords.min == [1.0, 2.0, 3.0, 4.0, 5.0]
    assert missing.min == [1.0, 2.0, 3.0, 4.0]
    assert single.min == 1.0

def test_max(coords, missing, single):
    assert coords.max == [55.0, 56.0, 57.0, 58.0, 59.0]
    assert missing.max == [52.0, 52.0, 52.0, 52.0]
    assert single.max == 35.0

def test_subset(coords):
    rect = Rectangle([(0,0), (2,0), (2,3), (0,3), (0,0)], None)
    assert (coords.subset(rect) == \
            np.array([[[  1.,   2.,   3.,   4.,   5.],
                       [ 21.,  21.,  21.,  21.,  21.]],
                      [[ 12.,  12.,  12.,  12.,  12.],
                       [ 22.,  22.,  22.,  22.,  22.]],
                      [[ 13.,  13.,  13.,  13.,  13.],
                       [ 23.,  23.,  23.,  23.,  23.]]])).all()


def test_mean(coords, missing, single):
    assert coords.mean == [32.6, 32.68, 32.76, 32.84, 32.92]
    assert missing.mean == [27.842105263157894,
                       27.894736842105264,
                       27.94736842105263,
                       28.0]
    assert single.mean == pytest.approx(22.3333333333)

def test_stddev(coords, missing, single):
    assert coords.stddev == [14.947909552843836,
                             14.925736162749226,
                             14.908467392726859,
                             14.896120300266107,
                             14.88870712990218]

    assert missing.stddev == [13.554036718164102,
                              13.451256004129974,
                              13.351418943754043,
                              13.254592054315205]

    assert single.stddev == 9.5335664307167285

def test_get_data_returns_masked_array(coords):
    assert isinstance(coords.get_data(), np.ma.core.MaskedArray)

def test_get_data_masked_false_returns_ndarray(missing):
    assert isinstance(missing.get_data(maksed=False), np.ndarray)

def test_get_data_single_band(single):
    assert (single.get_data() == \
            np.array([[  1.,  21.,  31.],
                      [ 12.,  22.,  32.],
                      [ 13.,  23.,  33.],
                      [ 14.,  24.,  34.],
                      [ 15.,  25.,  35.]])).all()

def test_shape(coords):
    assert hasattr(coords.shape, "exterior")
    assert hasattr(coords.shape.exterior, "coords")
    assert list(coords.shape.exterior.coords) == [(0.0, 0.0), (5.0, 0.0), (5.0, 5.0), (0.0, 5.0), (0.0, 0.0)]

def test_ix(coords, single):
    assert coords.ix(0,0) == [ 1.0, 2.0, 3.0, 4.0, 5.0]
    assert single.ix(0,0) == 1.

def test_get_data_shape(rect):
    assert rect.get_data().shape == (5, 3, 2)
    assert rect.get_data(axis=0).shape == (2, 5, 3)
    assert rect.get_data(axis=1).shape == (5, 2, 3)
    assert rect.get_data(axis=2).shape == (5, 3, 2)

def test_get_data_value(rect):
    assert (rect.get_data() == \
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


def test_window(rect, coords):
    assert \
        (rect.get_data(window=((1,1), (3,2))) == \
         np.array([[[ 22.,  22.],
                    [ 32.,  32.]]])).all()


    assert \
        (coords.get_data(window=((2,2), (5,4))) == \
         np.array([[[ 33.,  33.,  33.,  33.,  33.],
                    [ 43.,  43.,  43.,  43.,  43.],
                    [ 53.,  53.,  53.,  53.,  53.]],
                   [[ 34.,  34.,  34.,  34.,  34.],
                    [ 44.,  44.,  44.,  44.,  44.],
                    [ 54.,  54.,  54.,  54.,  54.]]])).all()


def test_nonmasked_array(missing):
    assert (missing.get_data(masked=False) == \
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




def test_masked_array(missing):
    assert \
        (missing.get_data().mask == \
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



def test_getitem_list_returns_raster_data(coords):
    assert isinstance(coords[1,2,3], RasterData)
    assert len(coords[1,2,3]) == 3


def test_getitem_int_returns_raster_data(coords):
    assert isinstance(coords[1], RasterData)
    assert len(coords[1]) == 1

def test_getitem_bad_throws_exception(coords):
    with pytest.raises(AssertionError):
        coords[0]

    with pytest.raises(AssertionError):
        coords[[0, 1, 2]]

    with pytest.raises(IndexError):
        coords['foo']

    with pytest.raises(IndexError):
        coords[['foo', 'bar', 'baz']]


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
