import xml.etree.ElementTree as ET
import unittest

import mock

from geonotebook.vis.geoserver import sld


class TestMultiBandParams(unittest.TestCase):

    @mock.patch("geonotebook.vis.geoserver.sld.SLDTemplates")
    def test_assigned_name_is_passed_correctly(self, templates):
        """ If name is given template_params['name'] should
        be the same as the given name """

        render = templates.get_template.return_value.render
        name = 'Super Fancy Name'
        multiband_xml = sld.get_multiband_raster_sld(name)

        self.assertEquals(render.call_args[1]['name'], name)

    @mock.patch("geonotebook.vis.geoserver.sld.SLDTemplates")
    def test_deafault_title(self, templates):
        """ If title is None template_params['title']
        should still be a string """

        render = templates.get_template.return_value.render
        name = 'Some_Name'
        multiband_xml = sld.get_multiband_raster_sld(name)

        self.assertTrue(type(render.call_args[1]['title']) == str)

    @mock.patch("geonotebook.vis.geoserver.sld.SLDTemplates")
    def test_title_is_passed_correctly(self, templates):
        """ If title is passed in template_params['title']
        should equal that string """

        render = templates.get_template.return_value.render
        name = 'Some_Name'
        title = 'Tiff_Title'
        multiband_xml = sld.get_multiband_raster_sld(name,
                                                     title=title)

        self.assertEquals(render.call_args[1]['title'], title)

    @mock.patch("geonotebook.vis.geoserver.sld.SLDTemplates")
    def test_title_exists_in_template_params(self, templates):
        """ if title not passed in template_params
        should have a title attr """

        render = templates.get_template.return_value.render
        name = 'Some_Name'
        multiband_xml = sld.get_multiband_raster_sld(name)

        self.assertTrue('title' in render.call_args[1])

    def test_band_is_a_list_or_tuple(self):
        """ If bands is not a list/tuple should
        throw an exception """

        name = 'Some_Name'
        bands = 'Wrong Band Type'

        self.assertRaises(AssertionError, sld.get_multiband_raster_sld,
                          name, bands=bands)

    def test_band_values_are_greater_than_zero(self):
        """ If any value of bands is less than 1
        should throw an exception """

        name = 'Some_Name'
        bands = [1, 2, -1]

        self.assertRaises(AssertionError, sld.get_multiband_raster_sld,
                          name, bands=bands)

    def test_band_values_are_integers(self):
        """ If any value of bands is not an
        integer, should throw an exception """

        name = 'Some_Name'
        bands = [1, 1.3, 2.0]

        self.assertRaises(AssertionError, sld.get_multiband_raster_sld,
                          name, bands=bands)

    @mock.patch("geonotebook.vis.geoserver.sld.SLDTemplates")
    def test_number_of_bands_are_correct(self, templates):
        """ If 3 bands are passed there must be 3 channels """

        render = templates.get_template.return_value.render
        name = 'Some_Name'
        bands = (1, 2, 3)
        multiband_xml = sld.get_multiband_raster_sld(name,
                                                     bands=bands)
        num_of_bands = render.call_args[1]['channels']

        self.assertEquals(len(num_of_bands), 3)

    def test_band_numbers_must_be_three(self):
        """ Given number of bands must be equal to 3 """

        name = 'Some_Name'
        bands = [4, 5, 6, 9, 12]

        self.assertRaises(AssertionError, sld.get_multiband_raster_sld,
                          name, bands=bands)

    @mock.patch("geonotebook.vis.geoserver.sld.SLDTemplates")
    def test_given_band_values_are_set_correctly(self, templates):
        """ Given band order must match with channel's band properties """

        render = templates.get_template.return_value.render
        name = 'Some_Name'
        bands = [9, 5, 2]
        multiband_xml = sld.get_multiband_raster_sld(name,
                                                     bands=bands)
        out_bands = [i['band'] for i in render.call_args[1]['channels']]

        self.assertEquals(bands, out_bands)

    @mock.patch("geonotebook.vis.geoserver.sld.SLDTemplates")
    def test_default_single_range_is_applied_to_all_bands(self, templates):
        """ If range is not passed in and bands=(1,2,3)
        template_params['range'] should equal [(0,1), (0,1), (0,1)] """

        render = templates.get_template.return_value.render
        name = 'Some_Name'
        multiband_xml = sld.get_multiband_raster_sld(name)
        ranges = [(i['options']['minValue'], i['options']['maxValue'])
                  for i in render.call_args[1]['channels']]

        self.assertEquals(ranges, [(0, 1), (0, 1), (0, 1)])

    @mock.patch("geonotebook.vis.geoserver.sld.SLDTemplates")
    def test_given_single_range_is_applied_to_all_bands(self, templates):
        """ If range is passed in as tuple (10, 20) and bands=(1,2,3)
        template_params['range'] should equal [(10,20), (10,20), (10,20)] """

        render = templates.get_template.return_value.render
        name = 'Some_Name'
        range = (10, 20)
        multiband_xml = sld.get_multiband_raster_sld(name,
                                                     range=range)
        ranges = [(i['options']['minValue'], i['options']['maxValue'])
                  for i in render.call_args[1]['channels']]

        self.assertEquals(ranges, [(10, 20), (10, 20), (10, 20)])

    @mock.patch("geonotebook.vis.geoserver.sld.SLDTemplates")
    def test_given_multi_range_is_applied_correctly(self, templates):
        """ If range is passed in as a list of tuples
        [(10,20), (40,50), (90,100)] and bands=(1,2,3)
        template_params['range'] should equal
        to [(10,20), (40,50), (90,100)] """

        render = templates.get_template.return_value.render
        name = 'Some_Name'
        ranges = [(10, 20), (40, 50), (90, 100)]
        multiband_xml = sld.get_multiband_raster_sld(name,
                                                     range=ranges)
        out_ranges = [(i['options']['minValue'], i['options']['maxValue'])
                      for i in render.call_args[1]['channels']]

        self.assertEquals(ranges, out_ranges)

    def test_number_of_ranges_is_equal_to_number_of_bands(self):
        """ If range is passed in as a list [(0,1),(0,1)] and
        bands (1,2,3) should throw an exception """

        name = 'Some_Name'
        ranges = [(0, 1), (1, 2)]

        self.assertRaises(AssertionError, sld.get_multiband_raster_sld,
                          name, range=ranges)

    def test_ranges_must_have_two_values(self):
        """ If ranges has more or less then two
        elements, should throw an exception """

        name = 'Some_Name'
        ranges_1 = (0, 1, 2)
        ranges_2 = [(0, 1, 2), (0, 3, 4), (0)]

        self.assertRaises(AssertionError, sld.get_multiband_raster_sld,
                          name, range=ranges_1)

        self.assertRaises(AssertionError, sld.get_multiband_raster_sld,
                          name, range=ranges_2)


    def test_gamma_is_a_number(self):
        """ If gamma is not passed as a number thrown an
        exception """

        name = 'Some_Name'
        # Give a string with length of 3
        expected_gamma = 'Gam'

        self.assertRaises(AssertionError, sld.get_multiband_raster_sld,
                          name, gamma=expected_gamma)

    def test_number_of_gamma_is_equal_to_number_of_bands(self):
        """ If gamma is passed in as list [0.1, 0.2] and bands (1,2,3)
        should throw an exception """

        name = 'Some_Name'
        gamma = [0.1, 0.2]

        self.assertRaises(AssertionError, sld.get_multiband_raster_sld,
                          name, gamma=gamma)

    @mock.patch("geonotebook.vis.geoserver.sld.SLDTemplates")
    def test_default_gamma_is_applied_to_all_bands(self, templates):
        """ If gamma is not passed in and bands=(1,2,3)
        template_params['gamma'] should equal [(1.0), (1.0), (1.0)] """

        render = templates.get_template.return_value.render
        name = 'Some_Name'
        multiband_xml = sld.get_multiband_raster_sld(name)
        gamma = [i['options']['gamma'] for i in render.call_args[1]['channels']]

        self.assertEquals(gamma, [(1.0), (1.0), (1.0)])

    @mock.patch("geonotebook.vis.geoserver.sld.SLDTemplates")
    def test_given_gamma_is_applied_to_all_bands(self, templates):
        """ If gamma is given 1.5 in and bands=(1,2,3)
        template_params['gamma'] should equal [(1.5), (1.5), (1.5)] """

        render = templates.get_template.return_value.render
        name = 'Some_Name'
        gamma = 1.5
        multiband_xml = sld.get_multiband_raster_sld(name,
                                                     gamma=gamma)
        gamma = [i['options']['gamma'] for i in render.call_args[1]['channels']]

        self.assertEquals(gamma, [(1.5), (1.5), (1.5)])

    @mock.patch("geonotebook.vis.geoserver.sld.SLDTemplates")
    def test_given_multi_gamma_is_applied_correctly(self, templates):
        """ If gamma is given as list [1.0, 1.5, 2.0]
        template_params['gamma'] should be equal to [1.0, 1.5, 2.0] """

        render = templates.get_template.return_value.render
        name= 'Some_Name'
        gammas = [1.0, 1.5, 2.0]
        multiband_xml = sld.get_multiband_raster_sld(name,
                                                     gamma=gammas)
        gammas_out = [i['options']['gamma'] for i in render.call_args[1]['channels']]

        self.assertEquals(gammas_out, gammas)

    def test_opacity_is_a_number(self):
        """ If opacity is not a number, should
        throw an exception """

        name = 'Some_Name'
        opacity = 'opacity'

        self.assertRaises(AssertionError, sld.get_multiband_raster_sld,
                          name, opacity=opacity)

    def test_opacity_is_between_0_and_1(self):
        """ Opacity must be between 0 and 1 """

        name = 'Some_Name'
        opacity_1 = 1.5
        opacity_2 = -0.5

        self.assertRaises(AssertionError, sld.get_multiband_raster_sld,
                          name, opacity=opacity_1)

        self.assertRaises(AssertionError, sld.get_multiband_raster_sld,
                          name, opacity=opacity_2)

    @mock.patch("geonotebook.vis.geoserver.sld.SLDTemplates")
    def test_default_opacity_is_applied_correctly(self, templates):
        """ If opacity is not provided it should default to 1.0 """

        render = templates.get_template.return_value.render
        name= 'Some_Name'
        multiband_xml = sld.get_multiband_raster_sld(name)
        opacity = render.call_args[1]['opacity']

        self.assertEquals(opacity, 1.0)

    @mock.patch("geonotebook.vis.geoserver.sld.SLDTemplates")
    def test_default_opacity_is_applied_correctly(self, templates):
        """ If opacity is provided as 0.7 it should be equal to 0.7 """

        render = templates.get_template.return_value.render
        name= 'Some_Name'
        opacity = 0.7
        multiband_xml = sld.get_multiband_raster_sld(name,
                                                     opacity=opacity)
        opacity_out = render.call_args[1]['opacity']

        self.assertEquals(opacity_out, opacity)


class TestSingleBandParams(unittest.TestCase):

    @mock.patch("geonotebook.vis.geoserver.sld.SLDTemplates")
    def test_assigned_name_is_passed_correctly(self, templates):
        """ If name is given template_params['name'] should
        be the same as the given name """

        render = templates.get_template.return_value.render
        name = 'Super Fancy Name'
        band = 1
        singleband_xml = sld.get_single_band_raster_sld(name, band)

        self.assertEquals(render.call_args[1]['name'], name)

    @mock.patch("geonotebook.vis.geoserver.sld.SLDTemplates")
    def test_deafault_title(self, templates):
        """ If title is None template_params['title']
        should still be a string """

        render = templates.get_template.return_value.render
        name = 'Some_Name'
        band = 1
        singleband_xml = sld.get_single_band_raster_sld(name, band)

        self.assertTrue(type(render.call_args[1]['title']) == str)

    @mock.patch("geonotebook.vis.geoserver.sld.SLDTemplates")
    def test_title_is_passed_correctly(self, templates):
        """ If title is passed in template_params['title']
        should equal that string """

        render = templates.get_template.return_value.render
        name = 'Some_Name'
        title = 'Tiff_Title'
        band = 1
        singleband_xml = sld.get_single_band_raster_sld(name, band,
                                                     title=title)

    def test_band_is_greater_than_zero(self):
        """ If band is less than 1
        should throw an exception """

        name = 'Some_Name'
        band = 0

        self.assertRaises(AssertionError, sld.get_single_band_raster_sld,
                          name, band=band)

    @mock.patch("geonotebook.vis.geoserver.sld.SLDTemplates")
    def test_given_band_value_is_set_correctly(self, templates):
        """ Given band must match with channel's band property """

        render = templates.get_template.return_value.render
        name = 'Some_Name'
        band = 1
        singleband_xml = sld.get_single_band_raster_sld(name, band)
        out_band = render.call_args[1]['channels'][0]['band']

        self.assertEquals(band, out_band)

    @mock.patch("geonotebook.vis.geoserver.sld.SLDTemplates")
    def test_name_exists_in_template_params(self, templates):
        """ Template params should have a name attribute """

        render = templates.get_template.return_value.render
        name = 'Some_Name'
        band = 1
        singleband_xml = sld.get_single_band_raster_sld(name, band)

        self.assertTrue('name' in render.call_args[1])

    @mock.patch("geonotebook.vis.geoserver.sld.SLDTemplates")
    def test_title_exists_in_template_params(self, templates):
        """ Template params should have a title attribute """

        render = templates.get_template.return_value.render
        name = 'Some_Name'
        band = 1
        singleband_xml = sld.get_single_band_raster_sld(name, band)

        self.assertTrue('title' in render.call_args[1])

    @mock.patch("geonotebook.vis.geoserver.sld.SLDTemplates")
    def test_opacity_exists_in_template_params(self, templates):
        """ Template params should have a opacity attribute """

        render = templates.get_template.return_value.render
        name = 'Some_Name'
        band = 1
        singleband_xml = sld.get_single_band_raster_sld(name, band)

        self.assertTrue('opacity' in render.call_args[1])

    @mock.patch("geonotebook.vis.geoserver.sld.SLDTemplates")
    def test_opacity_exists_in_template_params(self, templates):
        """ Template params should have a channels attribute """

        render = templates.get_template.return_value.render
        name = 'Some_Name'
        band = 1
        singleband_xml = sld.get_single_band_raster_sld(name, band)

        self.assertTrue('channels' in render.call_args[1])

    @mock.patch("geonotebook.vis.geoserver.sld.SLDTemplates")
    def test_default_channel_name_is_passed_correctly(self, templates):
        """ if no custom channelName template_params['channels'][0]['name']
        should be equal to GrayChannel """

        render = templates.get_template.return_value.render
        name = 'Super Fancy Name'
        band = 1
        singleband_xml = sld.get_single_band_raster_sld(name, band)

        self.assertEquals(render.call_args[1]['channels'][0]['name'], 'GrayChannel')

    @mock.patch("geonotebook.vis.geoserver.sld.SLDTemplates")
    def test_assigned_channel_name_is_passed_correctly(self, templates):
        """ If custom channelName template_params['channels'][0]['name']
        should be equal to custom channelName """

        render = templates.get_template.return_value.render
        name = 'Super Fancy Name'
        band = 1
        channel_name = "Super Channel Name"
        singleband_xml = sld.get_single_band_raster_sld(name, band,
                                                        channelName=channel_name)

        self.assertEquals(render.call_args[1]['channels'][0]['name'], channel_name)

    @mock.patch("geonotebook.vis.geoserver.sld.SLDTemplates")
    def test_colormap_type_does_not_exist_in_template_params_by_default(self, templates):
        """ If no colormap_type is passed in no colormap_type
        attr should be in template_params
        """

        render = templates.get_template.return_value.render
        name = 'Some_Name'
        band = 1
        singleband_xml = sld.get_single_band_raster_sld(name, band)

        self.assertFalse('colormap_type' in render.call_args[1])

    @mock.patch("geonotebook.vis.geoserver.sld.SLDTemplates")
    def test_colormap_type_assigned_correctly(self, templates):
        """ If custom colormap_type is passed in
        template_params['colormap_type'] should be
        equal to custom colormap_type
        """

        render = templates.get_template.return_value.render
        name = 'Some_Name'
        band = 1
        colormap = [{"color": "#000000", "quantity": "0"},
                    {"color": "#0000FF", "quantity": "1"}]
        colormap_type = "Different ramp"
        singleband_xml = sld.get_single_band_raster_sld(name, band,
                                                        colormap=colormap,
                                                        colormap_type=colormap_type)

        self.assertEquals(colormap_type, render.call_args[1]['colormap_type'])

    @mock.patch("geonotebook.vis.geoserver.sld.SLDTemplates")
    def test_colormap_does_not_exist_in_template_params_by_default(self, templates):
        """ if colormap is None there should be no 'colormap'
        attribute in template_params """

        render = templates.get_template.return_value.render
        name = 'Some_Name'
        band = 1
        singleband_xml = sld.get_single_band_raster_sld(name, band)

        self.assertFalse('colormap' in render.call_args[1])

    def test_colormap_is_a_list_or_tuple(self):
        """ If colormap is not a list/tuple should throw an exception """

        name = 'Some_Name'
        band = 1
        colormap = "Not a List or Tuple"

        self.assertRaises(AssertionError, sld.get_single_band_raster_sld,
                          name, band, colormap=colormap)

    def test_colormap_is_a_collection_of_dictionaries(self):
        """ If colormap values are not all dicts should throw an exception """

        name = 'Some_Name'
        band = 1
        colormap = ["foo", "bar"]

        self.assertRaises(AssertionError, sld.get_single_band_raster_sld,
                          name, band, colormap=colormap)

    def test_each_colormap_element_has_color(self):
        """ If colormap values do not all contain 'color'
        attribute should thrown an exception """

        name = 'Some_Name'
        band = 1
        colormap = [{'foo': 'bar'},
                    {'bar': 'foo'}]

        self.assertRaises(AssertionError, sld.get_single_band_raster_sld,
                          name, band, colormap=colormap)

    def test_each_colormap_element_has_quantity(self):
        """ If colormap values do not all contain 'quantity'
        attribute should thrown an exception """

        name = 'Some_Name'
        band = 1
        colormap = [{'foo': 'bar'},
                    {'bar': 'foo'}]

        self.assertRaises(AssertionError, sld.get_single_band_raster_sld,
                          name, band, colormap=colormap)
