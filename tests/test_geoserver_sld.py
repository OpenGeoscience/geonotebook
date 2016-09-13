import xml.etree.ElementTree as ET
import unittest

from geonotebook.vis.geoserver import sld


class TestMultiBandParams(unittest.TestCase):

    @staticmethod
    def _find_xml_element(root, tag):
        """ Finds a tag and returns it's text """

        namespace = "{http://www.opengis.net/sld}"

        for elem in root.iter():
            if "{}{}".format(namespace, tag) == elem.tag:
                return elem.text

    def test_deafault_title(self):
        """ If title is None template
        should have the default string """

        name = 'Some_Name'
        multiband_xml = sld.get_multiband_raster_sld(name)
        root = ET.fromstring(multiband_xml.strip())
        xml_title = self._find_xml_element(root, 'Title')
        expected_title = "Style for bands 1,2,3 of layer {}".format(name)

        self.assertEquals(xml_title, expected_title)

    def test_title_is_passed_to_template_correctly(self):
        """ If title is passed in, template
        should have the passed value """

        name = 'Some_Name'
        expected_title = 'Fancy Title'
        multiband_xml = sld.get_multiband_raster_sld(name,
                                                     title=expected_title)
        root = ET.fromstring(multiband_xml.strip())
        xml_title = self._find_xml_element(root, 'Title')

        self.assertEquals(xml_title, expected_title)

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

    def test_given_band_values_are_set_correctly(self):
        """ Band Values should be set correctly """

        name = 'Some_Name'
        expected_bands = [4, 3, 9]
        multiband_xml = sld.get_multiband_raster_sld(name,
                                                     bands=expected_bands)
        namespace = "{http://www.opengis.net/sld}"
        xml_bands = []
        root = ET.fromstring(multiband_xml.strip())
        for elem in root.iter("{}{}".format(namespace, 'SourceChannelName')):
            xml_bands.append(int(float(elem.text)))

        self.assertEquals(expected_bands, xml_bands)

    def test_band_numbers_must_be_three(self):
        """ Given number of bands must be equal to 3 """

        name = 'Some_Name'
        bands = [4, 5, 6, 9, 12]

        self.assertRaises(AssertionError, sld.get_multiband_raster_sld,
                          name, bands=bands)


    def test_default_single_range_is_applied_to_all_bands(self):
        """ If range is passed in as tuple(0,1) and bands=(1,2,3)
        all bands have to have (0,1) range """

        name = 'Some_Name'
        multiband_xml = sld.get_multiband_raster_sld(name)
        root = ET.fromstring(multiband_xml.strip())

        namespace = "{http://www.opengis.net/sld}"

        expected_minimum = 0
        expected_maximum = 1

        xml_ranges = []
        for elem in root.iter("{}{}".format(namespace, 'VendorOption')):
            if elem.attrib['name'] == 'minValue':
                self.assertEquals(expected_minimum, int(elem.text))
            elif elem.attrib['name'] == 'maxValue':
                self.assertEquals(expected_maximum, int(elem.text))

    def test_given_single_range_is_applied_to_all_bands(self):
        """ If range is passed in as tuple(0,1) and bands=(1,2,3)
        all bands have to have (0,1) range """

        name = 'Some_Name'
        expected_minimum = 10
        expected_maximum = 200
        range = (expected_minimum, expected_maximum)
        multiband_xml = sld.get_multiband_raster_sld(name,
                                                     range=range)
        root = ET.fromstring(multiband_xml.strip())

        namespace = "{http://www.opengis.net/sld}"

        xml_ranges = []
        for elem in root.iter("{}{}".format(namespace, 'VendorOption')):
            if elem.attrib['name'] == 'minValue':
                self.assertEquals(expected_minimum, int(elem.text))
            elif elem.attrib['name'] == 'maxValue':
                self.assertEquals(expected_maximum, int(elem.text))

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

    def test_multi_ranges_are_assigned_correctly(self):
        """ Given ranges should be reflected correctly
        in the xml document """

        name = 'Some_Name'
        expected_ranges = [(9, 10), (1.3, 2.5), (30, 42)]
        namespace = "{http://www.opengis.net/sld}"
        multiband_xml = sld.get_multiband_raster_sld(name,
                                                     range=expected_ranges)
        root = ET.fromstring(multiband_xml.strip())
        min_ranges = []
        max_ranges = []

        for elem in root.iter("{}{}".format(namespace, 'VendorOption')):
            if elem.attrib['name'] == 'minValue':
                min_ranges.append(float(elem.text))
            elif elem.attrib['name'] == 'maxValue':
                max_ranges.append(float(elem.text))

        xml_ranges = zip(min_ranges, max_ranges)

        self.assertEquals(expected_ranges, xml_ranges)

    def test__default_gamma_is_applied_to_all_bands(self):
        """ If gamma is not passed in all
        bands should have a gamma value of 1.0 """

        name = 'Some_Name'
        expected_gamma = 1.0
        multiband_xml = sld.get_multiband_raster_sld(name)
        root = ET.fromstring(multiband_xml.strip())
        namespace = "{http://www.opengis.net/sld}"

        for elem in root.iter("{}{}".format(namespace, 'GammaValue')):
            self.assertEquals(str(expected_gamma), elem.text)

    def test_given_single_gamma_is_applied_to_all_bands(self):
        """ If gamma is passed in as 0.3 and bands=(1,2,3) all
        bands should have a gamma value of 0.3 """

        name = 'Some_Name'
        expected_gamma = 0.3
        multiband_xml = sld.get_multiband_raster_sld(name,
                                                     gamma=expected_gamma)
        root = ET.fromstring(multiband_xml.strip())
        namespace = "{http://www.opengis.net/sld}"

        for elem in root.iter("{}{}".format(namespace, 'GammaValue')):
            self.assertEquals(str(expected_gamma), elem.text)


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

    def test_multiple_gamma_values_are_assigned_correctly(self):
        """ Multiple gamma values should be assigned correctly """

        name = 'Some_Name'
        expected_gamma = [0.3, 0.5, 0.7]
        multiband_xml = sld.get_multiband_raster_sld(name,
                                                     gamma=expected_gamma)
        root = ET.fromstring(multiband_xml.strip())
        namespace = "{http://www.opengis.net/sld}"

        xml_gamma = []

        for elem in root.iter("{}{}".format(namespace, 'GammaValue')):
            xml_gamma.append(float(elem.text))

        self.assertEquals(expected_gamma, xml_gamma)

    def test_name_is_passed_to_template_correctly(self):
        """ If name is passed in, template
        should have the passed value """

        expected_name = 'Some_Fancy_Name'
        multiband_xml = sld.get_multiband_raster_sld(expected_name)

        root = ET.fromstring(multiband_xml.strip())
        xml_name = self._find_xml_element(root, 'Name')

        self.assertEquals(expected_name, xml_name)

    def test_opacity_is_a_number(self):
        """ If opacity is not a number, should
        throw an exception """

        name = 'Some_Name'
        opacity = 'opacity'

        self.assertRaises(AssertionError, sld.get_multiband_raster_sld,
                          name, opacity=opacity)

    def test_default_opacity(self):
        """ If opacity is not given it should default
        to 1.0 """

        name = 'Some_Name'
        multiband_xml = sld.get_multiband_raster_sld(name)
        expected_opacity = 1.0
        root = ET.fromstring(multiband_xml.strip())

        xml_opacity = self._find_xml_element(root, 'Opacity')

        self.assertEquals(expected_opacity, float(xml_opacity))

    def test_given_opacity_is_assigned_correctly(self):
        """ If opacity is given, should be assigned correctly """

        name = 'Some_Name'
        expected_opacity = 0.5
        multiband_xml = sld.get_multiband_raster_sld(name,
                                                     opacity=expected_opacity)
        root = ET.fromstring(multiband_xml.strip())

        xml_opacity = self._find_xml_element(root, 'Opacity')

        self.assertEquals(expected_opacity, float(xml_opacity))

## Singleband
###
### if title is None template_params['title'] should still be a string
### if title is passed in template_params['title'] should equal that string
### if value of band is less than 1 should throw an exception
### if band=1 template_params['channels'][0]['band'] should be equal to 1
### template_params should have a name attr
### if title not passed in template_params should have a title attr
### if opacity not passed in template_params should have an opacity attr
### template_params should have a channels attr
### if no custom channelName template_params['channels'][0]['name'] should be equal to GrayChannel
### if custom channelName template_params['channels'][0]['name'] should be equal to custom channelName

### if no colormap_type is passed in no colormap_type attr should be in template_params
### if custom colormap_type is passed in template_params['colormap_type'] should be equal to custom colormap_type
### if colormap is None there should be no 'colormap' attribute in template_params
### if colormap is not a list/tuple should throw an exception
### if colormap values are not all dicts should throw an exception
### if colormap values do not all contain 'color' attribute should thrown an exception
### if colormap values do not all contain 'quantity' attribute should thrown an exception
