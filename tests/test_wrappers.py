import numpy as np
import pytest

from geonotebook.annotations import Rectangle
from geonotebook.wrappers import RasterData, RasterDataCollection

from . import wrappers_data
from .conftest import enable_mock


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
    rect = Rectangle([(0, 0), (2, 0), (2, 3), (0, 3), (0, 0)], None)
    assert (coords.subset(rect) == wrappers_data.subset).all()


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
    assert (single.get_data() == wrappers_data.single_band).all()


def test_shape(coords):
    assert hasattr(coords.shape, "exterior")
    assert hasattr(coords.shape.exterior, "coords")
    assert list(coords.shape.exterior.coords) == [
        (0.0, 0.0), (5.0, 0.0), (5.0, 5.0), (0.0, 5.0), (0.0, 0.0)
    ]


def test_ix(coords, single):
    assert coords.ix(0, 0) == [1.0, 2.0, 3.0, 4.0, 5.0]
    assert single.ix(0, 0) == 1.


def test_get_data_shape(rect):
    assert rect.get_data().shape == (5, 3, 2)
    assert rect.get_data(axis=0).shape == (2, 5, 3)
    assert rect.get_data(axis=1).shape == (5, 2, 3)
    assert rect.get_data(axis=2).shape == (5, 3, 2)


def test_get_data_value(rect):
    assert (rect.get_data() == wrappers_data.data_value).all()


def test_window(rect, coords):
    assert \
        (rect.get_data(window=((1, 1), (3, 2))) ==
         np.array([[[22., 22.],
                    [32., 32.]]])).all()

    assert \
        (coords.get_data(window=((2, 2), (5, 4))) ==
         np.array([[[33., 33., 33., 33., 33.],
                    [43., 43., 43., 43., 43.],
                    [53., 53., 53., 53., 53.]],
                   [[34., 34., 34., 34., 34.],
                    [44., 44., 44., 44., 44.],
                    [54., 54., 54., 54., 54.]]])).all()


def test_nonmasked_array(missing):
    assert (missing.get_data(masked=False) ==
            wrappers_data.nonmasked_array).all()


def test_masked_array(missing):
    assert (missing.get_data().mask ==
            wrappers_data.masked_array).all()


def test_getitem_list_returns_raster_data(coords):
    assert isinstance(coords[1, 2, 3], RasterData)
    assert len(coords[1, 2, 3]) == 3


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


# RasterDataCollection

def test_rdc_incorrect_bands():
    with enable_mock():
        # index less than one
        with pytest.raises(AssertionError):
            RasterDataCollection(
                ["rect.mock", "rect.mock", "rect.mock"],
                indexes=[0, 1, 2])

        # index greater than len(rdc)
        with pytest.raises(AssertionError):
            RasterDataCollection(
                ["rect.mock", "rect.mock", "rect.mock"],
                indexes=[10])


def test_rdc_inconsistent_bands():
    with enable_mock():
        with pytest.raises(AssertionError):
            RasterDataCollection(
                ["rect.mock", "missing.mock"])


def test_rdc_inconsistent_bands_verify_false():
    with enable_mock():
        RasterDataCollection(
            ["single.mock", "missing.mock"], verify=False)
        assert True


def test_rdc_inconsistent_bands_verify_false_clip_to_first():
    with enable_mock():
        rdc = RasterDataCollection(
            ["single.mock", "missing.mock"], verify=False)

        assert len(rdc[0]) == 1

        # missing.mock has 5 bands,  but is clipped to 1 band
        # because single.mock only has one band
        assert len(rdc[1]) == 1


def test_rdc_iter(rdc_rect):
    for i, rd in enumerate(rdc_rect):
        assert rd.path == rdc_rect[i].path
        assert (rd.get_data() == rdc_rect[i].get_data()).all()


def test_rdc_len(rdc_rect):
    assert len(rdc_rect) == 3


def test_rdc_get_names(rdc_rect):
    assert rdc_rect.get_names() == ['rect1', 'rect2', 'rect3']


def test_rdc_getitem_int_index(rdc_rect):
    rd = rdc_rect[0]
    assert isinstance(rd, RasterData)
    assert rd.name == 'rect1'


def test_rdc_getitem_slice_index(rdc_rect):
    rdc = rdc_rect[0:1]
    assert isinstance(rdc, RasterDataCollection)
    assert rdc.get_names() == ['rect1']

    rdc = rdc_rect[0:2]
    assert isinstance(rdc, RasterDataCollection)
    assert rdc.get_names() == ['rect1', 'rect2']

    rdc = rdc_rect[::2]
    assert isinstance(rdc, RasterDataCollection)
    assert rdc.get_names() == ['rect1', 'rect3']


def test_rdc_getitme_bad_item(rdc_rect):
    with pytest.raises(IndexError):
        rdc_rect['foobar']

    with pytest.raises(IndexError):
        rdc_rect[['foo', 'bar']]


def test_rdc_shape(rdc_rect):
    assert hasattr(rdc_rect.shape, "exterior")
    assert hasattr(rdc_rect.shape.exterior, "coords")
    assert list(rdc_rect.shape.exterior.coords) == \
        [(0.0, 0.0), (5.0, 0.0), (5.0, 3.0), (0.0, 3.0), (0.0, 0.0)]


def test_rdc_min(rdc_rect, rdc_single, rdc_one):
    assert rdc_rect.min == [[12.0, 2.0], [12.0, 2.0], [12.0, 2.0]]
    assert rdc_one.min == [12.0, 2.0]
    assert rdc_single.min == [12.0, 12.0, 12.0]


def test_rdc_max(rdc_rect, rdc_single, rdc_one):
    assert rdc_rect.max == [[100.0, 35.0], [200.0, 35.0], [300.0, 35.0]]
    assert rdc_one.max == [100.0, 35.0]
    assert rdc_single.max == [100.0, 200.0, 300.0]


def test_rdc_mean(rdc_rect, rdc_single, rdc_one):
    assert rdc_rect.mean == [[pytest.approx(28.9333333333), 22.4],
                             [35.6, 22.4],
                             [pytest.approx(42.2666666667), 22.4]]
    assert rdc_one.mean == [pytest.approx(28.9333333333), 22.4]
    assert rdc_single.mean == [38.8, 58.8, 78.8]


def test_rdc_stddev(rdc_rect, rdc_single, rdc_one):
    assert rdc_rect.stddev == [[20.47263756551385, 9.3865151502922881],
                               [44.59715984977818, 9.3865151502922881],
                               [69.30460943464648, 9.3865151502922881]]
    assert rdc_one.stddev == [20.47263756551385, 9.3865151502922881]
    assert rdc_single.stddev == \
        [31.475281306659252, 70.983754009867155, 110.84535774372031]


def test_rdc_nodata():
    with enable_mock():
        rdc = RasterDataCollection(['missing.mock', 'missing.mock'])
        assert rdc.nodata == -9999.0


def test_rdc_ix(rdc_rect, rdc_one, rdc_single):
    assert (rdc_rect.ix(0, 0) == [[100., 2.],
                                  [200., 2.],
                                  [300., 2.]]).all()
    assert rdc_one.ix(0, 0) == [100., 2.]
    assert (rdc_single.ix(0, 0) == [100., 200., 300.]).all()


def test_rdc_get_data(rdc_rect):
    assert isinstance(rdc_rect.get_data(), np.ma.masked_array)
    assert (rdc_rect.get_data() ==
            wrappers_data.rdc_get_data).all()


def test_rdc_get_data_single_band(rdc_single):
    assert isinstance(rdc_single.get_data(), np.ma.masked_array)
    assert (rdc_single.get_data() ==
            wrappers_data.rdc_get_data_single_band).all()


def test_rdc_get_data_window(rdc_rect):
    assert (rdc_rect.get_data(window=((0, 0), (3, 2))) ==
            wrappers_data.rdc_get_data_window).all()


def test_rdc_get_data_window_single_band(rdc_single):
    assert (rdc_single.get_data(window=((0, 0), (3, 2))) ==
            wrappers_data.rdc_get_data_window_single_band).all()


def test_rdc_get_data_masked_false(rdc_rect, rdc_single):
    assert not isinstance(
        rdc_rect.get_data(masked=False), np.ma.masked_array)
    assert not isinstance(
        rdc_single.get_data(masked=False), np.ma.masked_array)


def test_rdc_index(rdc_rect, mocker):
    idx = mocker.spy(RasterData, 'index')
    assert rdc_rect.index(0, 0) == (0, 0)
    assert idx.call_count == 1
