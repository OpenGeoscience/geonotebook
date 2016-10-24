import os
import pytest
from geonotebook import layers, wrappers
import mock
from pytest_mock import mocker

DEFAULT_CONFIG = """
[default]
vis_server = geoserver

[geoserver]
username = admin
password = geoserver
url = http://0.0.0.0:8080/geoserver
"""

class RDMock(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture(autouse=True)
def geonotebook_ini(tmpdir):
    p = tmpdir.mkdir('config').join("geonotebook.ini")
    p.write(DEFAULT_CONFIG)
    os.environ["GEONOTEBOOK_INI"] = str(p)

@pytest.fixture
def visserver(mocker, monkeypatch):
    import geonotebook
    visserver = mocker.patch('geonotebook.vis.geoserver.geoserver.Geoserver')
    monkeypatch.setitem(geonotebook.config.Config._valid_vis_hash, 'geoserver', visserver)
    return visserver.return_value

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


def test_layer_reprs(visserver):
    assert str(layers.GeonotebookLayer('gnbl', None)) == "<GeonotebookLayer('gnbl')>"
    assert str(layers.AnnotationLayer('al', None, None)) == "<AnnotationLayer('al')>"
    assert str(layers.NoDataLayer('ndl', None, None)) == "<NoDataLayer('ndl')>"
    assert str(layers.DataLayer('dl', None, None, vis_url='bogus')) == "<DataLayer('dl')>"
    assert str(layers.SimpleLayer('sl', None, None, vis_url='bogus')) == "<SimpleLayer('sl')>"
    assert str(layers.TimeSeriesLayer('tsl', None, [RDMock(name='bogus_data')])) == \
        "<TimeSeriesLayer('tsl')>"


# Annotation layer tests
def test_annotation_layer_add_point_annotation(point_coords):
    al = layers.AnnotationLayer('al', None, None)
    al.add_annotation('point', point_coords, {})
    assert len(al.points) == 1
    assert al.points[0].layer == al
    assert len(al.points[0].coords) == 1


def test_annotation_layer_add_rect_annotation(rect_coords):
    al = layers.AnnotationLayer('al', None, None)
    al.add_annotation('rectangle', rect_coords, {})
    assert len(al.rectangles) == 1
    assert al.rectangles[0].layer == al
    assert len(al.rectangles[0].exterior.coords) == 5

def test_annotation_layer_add_poly_annotation(poly_coords):
    al = layers.AnnotationLayer('al', None, None)
    al.add_annotation('polygon', poly_coords, {})
    assert len(al.polygons) == 1
    assert al.polygons[0].layer == al
    assert len(al.polygons[0].exterior.coords) == 7


def test_annotation_layer_add_bad_annotation(poly_coords):
    al = layers.AnnotationLayer('al', None, None)
    with pytest.raises(RuntimeError):
        al.add_annotation('badtype', poly_coords, {})


# NoDataLayer
def test_nodata_layer(visserver):
    ndl = layers.NoDataLayer("ndl", None, "http://bogus_url.com")
    assert ndl.vis_url == "http://bogus_url.com"

    with pytest.raises(AttributeError):
        ndl.data

    assert visserver.ingest.call_count == 0
    assert visserver.get_params.call_count == 0

# DataLayer
def test_data_layer(visserver):
    data = RDMock(name="test_data.tif")
    dl = layers.DataLayer("dl", None, data)
    assert dl.name == "dl"
    assert dl.data == data

def test_data_layer_with_no_data_and_no_vis_url(visserver):
    with pytest.raises(AssertionError):
        layers.DataLayer("dl", None, None, vis_url=None)


# SimpleLayer
def test_simple_layer(visserver):
    data = RDMock(name='test_data.tif')
    visserver.ingest.return_value = 'http://bogus_url.com'

    sl = layers.SimpleLayer('sl', None, data)
    assert sl.data == data
    assert sl.vis_url == 'http://bogus_url.com'

    assert visserver.ingest.call_count == 1
    assert visserver.get_params.call_count == 1


def test_simple_layer_with_no_data_and_no_vis_url(visserver):
    with pytest.raises(AssertionError):
        layers.SimpleLayer("dl", None, None, vis_url=None)

def test_simple_layer_override_vis_url(visserver):
    visserver.ingest.return_value = "http://bogus_url.com"
    sl = layers.SimpleLayer("dl", None, RDMock(name="test_data.tif"),
                            vis_url="http://some_other_url.com")

    assert sl.vis_url == "http://some_other_url.com"
    assert visserver.ingest.call_count == 0

# TimeSeriesLayer
@pytest.fixture
def rasterdata_list():
    return [RDMock(name='test_data1.tif'),
            RDMock(name='test_data2.tif'),
            RDMock(name='test_data3.tif')]


def test_timeseries_layer(visserver, rasterdata_list):
    tsl = layers.TimeSeriesLayer('tsl', None, rasterdata_list)

    assert tsl.name == 'tsl'
    assert len(tsl.data) == 3
    assert tsl.current.name == "test_data1.tif"
    assert visserver.ingest.call_count == 1


def test_timeseries_layer_forward(mocker, visserver, rasterdata_list):
    # Setup
    visserver.ingest.return_value = "http://bogus_url.com/test_data1.tif"
    visserver.get_params.return_value = {'foo': 'bar'}

    tsl = layers.TimeSeriesLayer('tsl', None, rasterdata_list)

    # Don't try to make any remote calls! We set 'create' to True here
    # Because _remote's API is generated dynamically by the nbextension's
    # get_protocol.
    mocker.patch.object(tsl, '_remote',  create=True)

    # Test
    assert tsl.current.name == "test_data1.tif"
    assert visserver.ingest.call_count == 1

    # Check that params are set,  and that we got them from the visserver
    assert tsl.params == {'foo': 'bar'}
    assert visserver.get_params.call_count == 1

    # Setup
    visserver.ingest.return_value = "http://bogus_url.com/test_data2.tif"
    visserver.get_params.return_value = {'foo': 'bar1'}

    tsl.forward()

    # Test
    assert tsl.current.name == "test_data2.tif"
    assert visserver.ingest.call_count == 2

    # replace_wms_layer is called to update the visual layer on the geojs map
    assert tsl._remote.replace_wms_layer.call_count == 1
    assert visserver.get_params.call_count == 2
    tsl._remote.replace_wms_layer.assert_called_with(
        "tsl", "http://bogus_url.com/test_data2.tif", {'foo': 'bar1'})


    # Setup
    visserver.ingest.return_value = "http://bogus_url.com/test_data3.tif"
    visserver.get_params.return_value = {'foo': 'bar2'}

    tsl.forward()

    # Test
    assert tsl.current.name == "test_data3.tif"
    assert visserver.ingest.call_count == 3

    # replace_wms_layer is called to update the visual layer on the geojs map
    assert tsl._remote.replace_wms_layer.call_count == 2
    assert visserver.get_params.call_count == 3
    tsl._remote.replace_wms_layer.assert_called_with(
        "tsl", "http://bogus_url.com/test_data3.tif", {'foo': 'bar2'})


def test_timeseries_layer_backward(mocker, visserver, rasterdata_list):
    # Setup
    visserver.ingest.return_value = "http://bogus_url.com/test_data1.tif"
    visserver.get_params.return_value = {'foo': 'bar'}

    tsl = layers.TimeSeriesLayer('tsl', None, rasterdata_list)

    # Don't try to make any remote calls! We set 'create' to True here
    # Because _remote's API is generated dynamically by the nbextension's
    # get_protocol.
    mocker.patch.object(tsl, '_remote',  create=True)
    assert tsl.params == {'foo': 'bar'}

    visserver.ingest.return_value = "http://bogus_url.com/test_data2.tif"
    visserver.get_params.return_value = {'foo': 'bar1'}

    tsl.forward()

    ingest_preback = visserver.ingest.call_count
    param_preback = visserver.get_params.call_count

    tsl.backward()

    assert visserver.ingest.call_count == ingest_preback
    assert visserver.get_params.call_count == param_preback


def test_timeseries_layer_idx(mocker, visserver, rasterdata_list):
    # Setup
    visserver.ingest.return_value = "http://bogus_url.com/test_data1.tif"
    visserver.get_params.return_value = {'foo': 'bar'}

    tsl = layers.TimeSeriesLayer('tsl', None, rasterdata_list)

    # Don't try to make any remote calls! We set 'create' to True here
    # Because _remote's API is generated dynamically by the nbextension's
    # get_protocol.
    mocker.patch.object(tsl, '_remote',  create=True)
    assert tsl.params == {'foo': 'bar'}

    visserver.ingest.return_value = "http://bogus_url.com/test_data3.tif"
    visserver.get_params.return_value = {'foo': 'bar2'}

    tsl.idx(2)

    assert visserver.ingest.call_count == 2
    assert visserver.get_params.call_count == 2
    assert tsl._remote.replace_wms_layer.call_count == 1
    tsl._remote.replace_wms_layer.assert_called_with(
        "tsl", "http://bogus_url.com/test_data3.tif", {'foo': 'bar2'})


def test_timeseries_out_of_range(visserver, rasterdata_list):
    tsl = layers.TimeSeriesLayer('tsl', None, rasterdata_list)

    with pytest.raises(IndexError):
        tsl.idx(-1)

    with pytest.raises(IndexError):
        tsl.idx(4)
