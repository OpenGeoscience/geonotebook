import unittest

from geonotebook import layers


class TestGeonotebookStack(unittest.TestCase):

    def setUp(self):

        self.stack = self.generate_stack()

    def test_geonotebookstack_instantiated_with_geonotebooklayers(self):
        """ Instantiate GeonotebookStack with list of
        non GeonotebookLayers should throw Exception """

        wrong_layers = [1, 2, 3]

        self.assertRaises(AssertionError, layers.GeonotebookStack,
                          layers=wrong_layers)

    @staticmethod
    def generate_stack():
        """ Generates 3 geonotebook instances """

        foo = layers.GeonotebookLayer('foo', vis_url='vis')
        bar = layers.GeonotebookLayer('bar', vis_url='vis')
        baz = layers.GeonotebookLayer('baz', vis_url='vis')

        return layers.GeonotebookStack([foo, bar, baz])

    def test_geonotebookstack_has_geonotebooklayer_items(self):
        """ GeonotebookStack.find('foo') should return GeonotebookLayer """

        self.assertTrue(isinstance(self.stack.find('foo'),
                                   layers.GeonotebookLayer))

    def test_nonexistent_layer_returns_None(self):
        """ GeonotebookStack.find('derp') should return None """

        self.assertEquals(self.stack.find('derp'),
                          None)

    def test_lambda_expressions_with_find(self):
        """ GeonotebookStack.find(lambda g: g.name == 'foo')
        should return GeonotebookLayer """

        self.assertTrue(isinstance(self.stack.find(lambda g: g.name == 'foo'),
                                   layers.GeonotebookLayer))

    def test_lamba_find_with_non_existent_layer(self):
        """ GeonotebookStack.find(lambda g: g.name == 'derp')
        should return None """

        self.assertEquals(self.stack.find(lambda g: g.name == 'derp'),
                          None)

    def test_index_of_functionality(self):
        """ GeonoteobokStack.indexOf('foo') should return 0
        GeonoteobokStack.indexOf('bar') should return 1
        GeonoteobokStack.indexOf('baz') should return 2
        GeonoteobokStack.indexOf('derp') should return None """

        self.assertEquals(self.stack.indexOf('foo'), 0)
        self.assertEquals(self.stack.indexOf('bar'), 1)
        self.assertEquals(self.stack.indexOf('baz'), 2)
        self.assertEquals(self.stack.indexOf('derp'), None)

    def test_list_indexing_on_stack(self):
        """ GeonotebookStack[0] should return GeonotebookLayer
        and name should equal 'foo'
        """
        self.assertEquals(self.stack[0].name, 'foo')

    def test_dictionary_key_access_on_stack(self):
        """ GeonotebookStack['foo'] should return
        GeonotebookLayer and name should equal 'foo' """

        self.assertTrue(isinstance(self.stack['foo'], layers.GeonotebookLayer))
        self.assertEquals(self.stack['foo'].name, 'foo')





