import pytest
import numpy as np
from geonotebook import annotations

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

    expected = {'rect': [22.0, 22.0],
                'coords': [22.0, 22.0, 22.0, 22.0, 22.0],
                'single': 22.0,
                'missing': [22.0, 22.0, 22.0, 22.0]}

    for i, (layer, data) in enumerate(a.data):
        assert layer == glc_annotation[i]
        assert data == expected[layer.name]


def test_rect_data(glc_annotation):
    a = annotations.Rectangle([(0,0), (2,0), (2,2), (0,2), (0,0)], None,
                              layer=glc_annotation.annotation)
    expected = { 'rect': [[[  1.,  2.],
                           [ 21., 21.]],
                          [[ 12., 12.],
                           [ 22., 22.]]],
                 'coords': [[[  1.,  2.,  3.,  4.,  5.],
                             [ 21., 21., 21., 21., 21.]],
                            [[ 12., 12., 12., 12., 12.],
                             [ 22., 22., 22., 22., 22.]]],
                 'single': [[  1., 21.],
                            [ 12., 22.]],
                 'missing': [[[  1.,  2.,  3.,  4.],
                              [ 21., 21., 21., 21.]],
                             [[ 12., 12., 12., 12.],
                              [ 22., 22., 22., 22.]]] }

    for i, (layer, data) in enumerate(a.data):
        assert layer == glc_annotation[i]
        assert (data == expected[layer.name]).all()


def test_polygon_data(glc_annotation):
    a = annotations.Polygon([(0,0), (3,3), (3,0), (0,0)], None,
                            layer=glc_annotation.annotation)
    expected = {
        'rect': np.ma.masked_array(
            data=[[[1.0, 2.0], [-9999., -9999.], [-9999.,  -9999.]],
                  [[12., 12.], [   22.,    22.], [-9999.,  -9999.]],
                  [[13., 13.], [   23.,    23.], [   33.,     33.]]],
            mask=[[[False, False], [ True,  True], [ True, True]],
                  [[False, False], [False, False], [ True, True]],
                  [[False, False], [False, False], [False, False]]],
            fill_value = -9999.0),

        'coords': np.ma.masked_array(
            data = [[[ 1.0,  2.0,  3.0,  4.0,  5.0], [-9999., -9999., -9999., -9999., -9999.], [-9999., -9999., -9999., -9999., -9999.]],
                    [[12.0, 12.0, 12.0, 12.0, 12.0], [   22.,    22.,    22.,    22.,    22.], [-9999., -9999., -9999., -9999., -9999.]],
                    [[13.0, 13.0, 13.0, 13.0, 13.0], [   23.,    23.,    23.,    23.,    23.], [   33.,    33.,    33.,    33.,    33.]]],
            mask = [[[False, False, False, False, False], [ True,  True,  True,  True,  True], [ True,  True,  True,  True,  True]],
                    [[False, False, False, False, False], [False, False, False, False, False], [ True,  True,  True,  True,  True]],
                    [[False, False, False, False, False], [False, False, False, False, False], [False, False, False, False, False]]],
            fill_value = -9999.0),

        'single': np.ma.masked_array(
            data = [[ 1., -9999., -9999.],
                    [12.,    22., -9999.],
                    [13.,    23.,    33.]],
            mask =[[False,  True,  True],
                   [False, False,  True],
                   [False, False, False]],
            fill_value = -9999.0),

        'missing': np.ma.masked_array(
            data = [[[ 1.,  2.,  3.,  4.], [-9999., -9999., -9999., -9999.], [-9999., -9999., -9999., -9999.]],
                    [[12., 12., 12., 12.], [   22.,    22.,    22.,    22.], [-9999., -9999., -9999., -9999.]],
                    [[13., 13., 13., 13.], [   23.,    23.,    23.,    23.], [   33.,    33.,    33.,    33.]]],
            mask = [[[False, False, False, False], [ True,  True,  True,  True], [ True,  True,  True,  True]],
                    [[False, False, False, False], [False, False, False, False], [ True,  True,  True,  True]],
                    [[False, False, False, False], [False, False, False, False], [False, False, False, False]]],
            fill_value = -9999.0)
        }


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
