import sys

import pytest

from geonotebook import layers
from .conftest import RDMock

pytestmark = pytest.mark.usefixtures("geonotebook_ini")


def test_layer_reprs(visserver):
    assert str(layers.GeonotebookLayer('gnbl', None, None)) == \
        "<GeonotebookLayer('gnbl')>"
    assert str(layers.AnnotationLayer('al', None, None)) == \
        "<AnnotationLayer('al')>"
    assert str(layers.NoDataLayer('ndl', None, None)) == "<NoDataLayer('ndl')>"
    assert str(layers.DataLayer('dl', None, None, vis_url='bogus')) == \
        "<DataLayer('dl')>"
    assert str(layers.SimpleLayer('sl', None, None, vis_url='bogus')) == \
        "<SimpleLayer('sl')>"
    assert str(
        layers.TimeSeriesLayer('tsl', None, [RDMock(name='bogus_data')])
    ) == \
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


def test_simple_layer_with_no_data_and_no_vis_url(visserver):
    with pytest.raises(AssertionError):
        layers.SimpleLayer("dl", None, None, vis_url=None)


def test_simple_layer_override_vis_url(visserver):
    visserver.ingest.return_value = "http://bogus_url.com"
    sl = layers.SimpleLayer("dl", None, RDMock(name="test_data.tif"),
                            vis_url="http://some_other_url.com")

    assert sl.vis_url == "http://some_other_url.com"
    assert visserver.ingest.call_count == 0


def test_timeseries_layer(visserver, rasterdata_list):
    tsl = layers.TimeSeriesLayer('tsl', None, rasterdata_list)

    assert tsl.name == '{}_{}_{}'.format(
        'tsl', rasterdata_list[0].name,
        hash(tsl.vis_options) + sys.maxsize + 1)
    assert len(tsl.data) == 3
    assert tsl.current.name == "test_data1.tif"
    assert visserver.ingest.call_count == 1


def test_timeseries_layer_forward(mocker, visserver, rasterdata_list):
    # Setup
    visserver.ingest.return_value = "http://bogus_url.com/test_data1"
    visserver.get_params.return_value = {'foo': 'bar'}

    tsl = layers.TimeSeriesLayer('tsl', None, rasterdata_list)

    # Don't try to make any remote calls! We set 'create' to True here
    # Because _remote's API is generated dynamically by the nbextension's
    # get_protocol.
    mocker.patch.object(tsl, '_remote', create=True)
    vis_options = mocker.patch.object(tsl, 'vis_options')
    vis_options.serialize.return_value = {'vis': 'options'}

    # Test
    assert tsl.current.name == "test_data1.tif"
    assert visserver.ingest.call_count == 1

    # Check that params are set,  and that we got them from the visserver
    assert tsl.query_params == {'foo': 'bar'}
    assert visserver.get_params.call_count == 1

    # Setup
    visserver.ingest.return_value = "http://bogus_url.com/test_data2"
    visserver.get_params.return_value = {'foo': 'bar1'}

    pre_name = tsl.name

    tsl.forward()

    post_name = tsl.name

    # Test
    assert tsl.current.name == "test_data2.tif"
    assert visserver.ingest.call_count == 2

    # replace_layer is called to update the visual layer on the geojs map
    assert tsl._remote.replace_layer.call_count == 1
    assert visserver.get_params.call_count == 2

    tsl._remote.replace_layer.assert_called_with(
        pre_name, post_name, "http://bogus_url.com/test_data2",
        {'vis': 'options'}, {'foo': 'bar1'})

    # Setup
    visserver.ingest.return_value = "http://bogus_url.com/test_data3"
    visserver.get_params.return_value = {'foo': 'bar2'}

    pre_name = tsl.name

    tsl.forward()

    post_name = tsl.name

    # Test
    assert tsl.current.name == "test_data3.tif"
    assert visserver.ingest.call_count == 3

    # replace_layer is called to update the visual layer on the geojs map

    assert tsl._remote.replace_layer.call_count == 2
    assert visserver.get_params.call_count == 3
    tsl._remote.replace_layer.assert_called_with(
        pre_name, post_name, "http://bogus_url.com/test_data3",
        {'vis': 'options'}, {'foo': 'bar2'})


def test_timeseries_layer_backward(mocker, visserver, rasterdata_list):
    # Setup
    visserver.ingest.return_value = "http://bogus_url.com/test_data1"
    visserver.get_params.return_value = {'foo': 'bar'}

    tsl = layers.TimeSeriesLayer('tsl', None, rasterdata_list)

    # Don't try to make any remote calls! We set 'create' to True here
    # Because _remote's API is generated dynamically by the nbextension's
    # get_protocol.
    mocker.patch.object(tsl, '_remote', create=True)

    vis_options = mocker.patch.object(tsl, 'vis_options')
    vis_options.serialize.return_value = {'vis': 'options'}

    assert tsl.query_params == {'foo': 'bar'}

    visserver.ingest.return_value = "http://bogus_url.com/test_data2"
    visserver.get_params.return_value = {'foo': 'bar1'}

    tsl.forward()

    ingest_preback = visserver.ingest.call_count
    param_preback = visserver.get_params.call_count

    tsl.backward()

    assert visserver.ingest.call_count == ingest_preback
    assert visserver.get_params.call_count == param_preback + 1


def test_timeseries_layer_idx(mocker, visserver, rasterdata_list):
    # Setup
    visserver.ingest.return_value = "http://bogus_url.com/test_data1"

    tsl = layers.TimeSeriesLayer('tsl', None, rasterdata_list)

    # Don't try to make any remote calls! We set 'create' to True here
    # Because _remote's API is generated dynamically by the nbextension's
    # get_protocol.
    mocker.patch.object(tsl, '_remote', create=True)
    vis_options = mocker.patch.object(tsl, 'vis_options')
    vis_options.serialize.return_value = {'vis': 'options'}

    visserver.ingest.return_value = "http://bogus_url.com/test_data3"
    visserver.get_params.return_value = {'query': 'params'}

    prev_name = tsl.name

    tsl.idx(2)

    cur_name = tsl.name
    assert visserver.ingest.call_count == 2
    assert visserver.get_params.call_count == 1
    assert tsl._remote.replace_layer.call_count == 1

    tsl._remote.replace_layer.assert_called_with(
        prev_name, cur_name, "http://bogus_url.com/test_data3",
        {'vis': 'options'}, {'query': 'params'})


def test_timeseries_out_of_range(visserver, rasterdata_list):
    tsl = layers.TimeSeriesLayer('tsl', None, rasterdata_list)

    with pytest.raises(IndexError):
        tsl.idx(-1)

    with pytest.raises(IndexError):
        tsl.idx(4)
