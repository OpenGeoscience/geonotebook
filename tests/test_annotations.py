import pytest
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


def test_point_data(glc_annotation):
    a = annotations.Point(1, 1, layer=glc_annotation.annotation)

    expected = {'rect': [22.0, 22.0],
                'coords': [22.0, 22.0, 22.0, 22.0, 22.0],
                'single': 22.0,
                'missing': [22.0, 22.0, 22.0, 22.0]}

    for i, (layer, data) in enumerate(a.data):
        assert layer == glc_annotation[i]
        assert data == expected[layer.name]


#def test_point_data_out_of_bounds(glc_annotation):
#    a = annotations.Point(100, 100, layer=glc_annotation.annotation)
#    import rpdb; rpdb.set_trace()
#    for i, (layer, data) in enumerate(a.data):
#        assert layer == glc_annotation[i]
#        assert data == expected[layer.name]

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
