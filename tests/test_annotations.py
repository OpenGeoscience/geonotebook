import pytest

from geonotebook import annotations

from . import annotations_data


def test_annotation_layer_kwarg(geonotebook_layer):
    a = annotations.Annotation(layer=geonotebook_layer)
    assert a.layer == geonotebook_layer


def test_annotation_kwarg_properties(geonotebook_layer):
    a = annotations.Annotation(
        **{'id': 1,
           'name': 'foo',
           'rgb': '#db5f57',
           'layer': geonotebook_layer})

    assert a.id == 1
    assert a.name == 'foo'
    assert a.rgb == '#db5f57'
    assert a.layer == geonotebook_layer


def test_annotation_kwarg_property_setters(geonotebook_layer):
    a = annotations.Annotation(
        **{'id': 1,
           'name': 'foo',
           'rgb': '#db5f57',
           'layer': geonotebook_layer})

    a.rgb = "#000000"
    assert a.rgb == "#000000"


def test_point_data(glc_annotation):
    a = annotations.Point(1, 1, layer=glc_annotation.annotation)

    expected = annotations_data.point

    for i, (layer, data) in enumerate(a.data):
        assert layer == glc_annotation[i]
        assert (data == expected[layer.name]).all()


def test_rect_data(glc_annotation):
    a = annotations.Rectangle(
        [(0, 0), (1.9, 0), (1.9, 1.9), (0, 1.9), (0, 0)],
        None, layer=glc_annotation.annotation
    )
    expected = annotations_data.rect

    for i, (layer, data) in enumerate(a.data):
        assert layer == glc_annotation[i]
        print(data)
        print(expected[layer.name])
        assert (data == expected[layer.name]).all()


def test_polygon_data(glc_annotation):
    a = annotations.Polygon([(0, 0), (3, 3), (3, 0), (0, 0)], None,
                            layer=glc_annotation.annotation)
    expected = annotations_data.polygon

    for i, (layer, data) in enumerate(a.data):
        assert layer == glc_annotation[i]
        assert (data == expected[layer.name]).all()


@pytest.mark.skip(reason="Still needs to be implemented")
def test_point_outside_data_bounds():
    pass


@pytest.mark.skip(reason="Still needs to be implemented")
def test_rectangle_outside_data_bounds():
    pass


@pytest.mark.skip(reason="Still needs to be implemented")
def test_polygon_outside_data_bounds():
    pass


@pytest.mark.skip(reason="Still needs to be implemented")
def test_rectangle_overlapping_data_bounds():
    pass


@pytest.mark.skip(reason="Still needs to be implemented")
def test_polygon_overlapping_data_bounds():
    pass


@pytest.mark.skip(reason="Still needs to be implemented")
def test_point_over_missing_data():
    pass


@pytest.mark.skip(reason="Still needs to be implemented")
def test_rectangle_overlapping_missing_data():
    pass


@pytest.mark.skip(reason="Still needs to be implemented")
def test_polygon_overlapping_missing_data():
    pass


@pytest.mark.skip(reason="Still needs to be implemented")
def test_rectangle_overlapping_missing_data_and_data_bounds():
    pass


@pytest.mark.skip(reason="Still needs to be implemented")
def test_polygon_overlapping_missing_data_and_data_bounds():
    pass
