import pytest
from geonotebook import layers

@pytest.fixture
def glc():
    """ glc: Geonotebook Layer Collection """

    foo = layers.GeonotebookLayer('foo', None, vis_url='vis')
    bar = layers.GeonotebookLayer('bar', None, vis_url='vis')
    baz = layers.GeonotebookLayer('baz', None, vis_url='vis')

    return layers.GeonotebookLayerCollection([foo, bar, baz])


def test_geonotebooklayercollection_instantiated_with_geonotebooklayers():
    """ Instantiate GeonotebookLayerCollection with list of
    non GeonotebookLayers should throw Exception """

    with pytest.raises(Exception):
        layers.GeonotebookLayerCollection([1, 2, 3])


def test_geonotebooklayercollection_has_geonotebooklayer_items(glc):
    """ GeonotebookLayerCollection.find('foo') should return GeonotebookLayer """

    assert isinstance(glc.find('foo'), layers.GeonotebookLayer)

def test_nonexistent_layer_returns_None(glc):
    """ GeonotebookLayerCollection.find('derp') should return None """
    assert glc.find('derp') is None


def test_lambda_expressions_with_find(glc):
    """ GeonotebookLayerCollection.find(lambda g: g.name == 'foo')
    should return GeonotebookLayer """

    assert isinstance(glc.find(lambda g: g.name == 'foo'),
                      layers.GeonotebookLayer)

def test_lamba_find_with_non_existent_layer(glc):
    """ GeonotebookLayerCollection.find(lambda g: g.name == 'derp')
    should return None """

    assert glc.find(lambda g: g.name == 'derp') is None

def test_list_indexing_on_layercollection(glc):
    """ GeonotebookLayerCollection[0] should return GeonotebookLayer
    and name should equal 'foo'
    """
    assert isinstance(glc[0], layers.GeonotebookLayer)
    assert glc[0].name == 'foo'

    assert isinstance(glc[1], layers.GeonotebookLayer)
    assert glc[1].name == 'bar'

    assert isinstance(glc[2], layers.GeonotebookLayer)
    assert glc[2].name == 'baz'

def test_list_indexing_index_error(glc):
    """ GeonotebookLayerCollection[0] should return GeonotebookLayer
    and name should equal 'foo'
    """
    with pytest.raises(IndexError):
        glc[4]

def test_dictionary_key_access_on_layercollection(glc):
    """ GeonotebookLayerCollection['foo'] should return
    GeonotebookLayer and name should equal 'foo' """

    assert isinstance(glc['foo'], layers.GeonotebookLayer)
    assert glc['foo'].name == 'foo'

    assert isinstance(glc['bar'], layers.GeonotebookLayer)
    assert glc['bar'].name == 'bar'

    assert isinstance(glc['baz'], layers.GeonotebookLayer)
    assert glc['baz'].name == 'baz'

def test_dictionary_key_access_key_error(glc):
    """ GeonotebookLayerCollection[0] should return GeonotebookLayer
    and name should equal 'foo'
    """
    with pytest.raises(KeyError):
        glc['derp']
