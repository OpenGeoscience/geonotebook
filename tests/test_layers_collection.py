import pytest
from geonotebook import layers


def test_geonotebooklayercollection_instantiated_with_geonotebooklayers():
    """ Instantiate GeonotebookLayerCollection with list of
    non GeonotebookLayers should throw Exception """

    with pytest.raises(Exception):
        layers.GeonotebookLayerCollection([1, 2, 3])

def test_layer_collection_length(glc):
    assert len(glc) == 3


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


def test_layer_collection_append_layer(glc):
    l = layers.GeonotebookLayer('test_layer', None)
    glc.append(l)

    assert glc['test_layer'] == l
    assert glc[-1] == l

def test_layer_collection_append_same_layer(glc):
    l = layers.GeonotebookLayer('test_layer', None)
    glc.append(l)

    with pytest.raises(Exception):
        glc.append(l)

def test_layer_collection_append_system_layer(glc):
    pre_length = len(glc)
    l = layers.GeonotebookLayer('test_layer', None, system_layer=True)
    glc.append(l)

    # System layers don't show up in length
    assert len(glc) == pre_length

    # System layers are not accessible via key index
    with pytest.raises(KeyError):
        glc['test_layer']

def test_layer_collection_append_same_system_layer(glc):
    l = layers.GeonotebookLayer('test_layer', None, system_layer=True)
    glc.append(l)

    with pytest.raises(Exception):
        glc.append(l)


def test_layer_collection_append_exposed_layer(glc):
    pre_length = len(glc)
    l = layers.GeonotebookLayer('test_layer', None, expose_as='test')
    glc.append(l)
    # Expose_as is not just for system layers
    assert glc['test_layer'] == l
    assert pre_length == len(glc) - 1

    assert glc.test == l


def test_layer_collection_append_exposed_layer_bad_attr(glc):
    l = layers.GeonotebookLayer('test_layer', None, expose_as='_layers')
    with pytest.raises(RuntimeError):
        glc.append(l)


def test_layer_collection_append_exposed_system_layer(glc):
    pre_length = len(glc)
    l = layers.GeonotebookLayer('test_layer', None,
                                system_layer=True, expose_as='test')
    glc.append(l)

    # System layers don't show up in length
    assert len(glc) == pre_length

    # System layers are not accessible via key index
    with pytest.raises(KeyError):
        glc['test_layer']

    # Test exposed attribute
    assert glc.test == l


def test_layer_collection_remove_layer_by_name(glc):
    glc.remove('foo')
    assert len(glc) == 2

    with pytest.raises(KeyError):
        glc['foo']

def test_layer_collection_remove_layer_by_layer(glc):
    l = glc.find('foo')
    glc.remove(l)
    assert len(glc) == 2

    with pytest.raises(KeyError):
        glc['foo']

def test_layer_collection_setitem(glc):
    l = layers.GeonotebookLayer('test_layer', None)
    glc['foo'] = l
    assert glc.find("foo") == l
    assert glc[0] == l

def test_layer_collection_setitem_with_int(glc):
    l = layers.GeonotebookLayer('test_layer', None)
    glc[0] = l
    assert glc.find("foo") == l
    assert glc[0] == l


def test_layer_collection_setitem_with_bad_value(glc):
    with pytest.raises(Exception):
        glc['foo'] = 'bar'

def test_layer_collection_setitem_with_system_layer(glc):
    l = layers.GeonotebookLayer('test_layer', None, system_layer=True)
    with pytest.raises(Exception):
        glc['test_layer'] = l


def test_layer_collection_repr(glc):
    assert str(glc) == "<GeonotebookLayerCollection("\
        "[<GeonotebookLayer('foo')>, <GeonotebookLayer('bar')>, " + \
        "<GeonotebookLayer('baz')>])>"
