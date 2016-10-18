import unittest

from geonotebook import layers


class TestGeonotebookLayerCollection(unittest.TestCase):

    def setUp(self):

        self.layer_collection = self.generate_layer_collection()

    def test_geonotebooklayercollection_instantiated_with_geonotebooklayers(self):
        """ Instantiate GeonotebookLayerCollection with list of
        non GeonotebookLayers should throw Exception """

        wrong_layers = [1, 2, 3]

        self.assertRaises(Exception, layers.GeonotebookLayerCollection,
                          layers=wrong_layers)

    @staticmethod
    def generate_layer_collection():
        """ Generates 3 geonotebook layer instances """

        foo = layers.GeonotebookLayer('foo', None, vis_url='vis')
        bar = layers.GeonotebookLayer('bar', None, vis_url='vis')
        baz = layers.GeonotebookLayer('baz', None, vis_url='vis')

        return layers.GeonotebookLayerCollection([foo, bar, baz])

    def test_geonotebooklayercollection_has_geonotebooklayer_items(self):
        """ GeonotebookLayerCollection.find('foo') should return GeonotebookLayer """

        self.assertTrue(isinstance(self.layer_collection.find('foo'),
                                   layers.GeonotebookLayer))

    def test_nonexistent_layer_returns_None(self):
        """ GeonotebookLayerCollection.find('derp') should return None """

        self.assertEquals(self.layer_collection.find('derp'),
                          None)

    def test_lambda_expressions_with_find(self):
        """ GeonotebookLayerCollection.find(lambda g: g.name == 'foo')
        should return GeonotebookLayer """

        self.assertTrue(isinstance(self.layer_collection.find(lambda g: g.name == 'foo'),
                                   layers.GeonotebookLayer))

    def test_lamba_find_with_non_existent_layer(self):
        """ GeonotebookLayerCollection.find(lambda g: g.name == 'derp')
        should return None """

        self.assertEquals(self.layer_collection.find(lambda g: g.name == 'derp'),
                          None)

    def test_list_indexing_on_layercollection(self):
        """ GeonotebookLayerCollection[0] should return GeonotebookLayer
        and name should equal 'foo'
        """
        self.assertEquals(self.layer_collection[0].name, 'foo')

    def test_dictionary_key_access_on_layercollection(self):
        """ GeonotebookLayerCollection['foo'] should return
        GeonotebookLayer and name should equal 'foo' """

        self.assertTrue(isinstance(self.layer_collection['foo'], layers.GeonotebookLayer))
        self.assertEquals(self.layer_collection['foo'].name, 'foo')
