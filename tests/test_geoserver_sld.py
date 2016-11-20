import matplotlib as mpl  # noqa
mpl.use('Agg')  # noqa

import xml.etree.ElementTree as ET

import pytest

from geonotebook.vis.geoserver import sld


@pytest.fixture
def render(mocker):
    templates = mocker.patch("geonotebook.vis.geoserver.sld.SLDTemplates")
    return templates.get_template.return_value.render


def test_assigned_name_is_passed_correctly(render):
    # If name is given template_params['name'] should
    # be the same as the given name

    name = 'Super Fancy Name'
    sld.get_multiband_raster_sld(name)

    assert render.call_args[1]['name'] == name


def test_default_title(render):
    # If title is None template_params['title']
    # should still be a string

    name = 'Some_Name'
    sld.get_multiband_raster_sld(name)

    assert type(render.call_args[1]['title']) == str


def test_title_is_passed_correctly(render):
    # If title is passed in template_params['title']
    # should equal that string

    name = 'Some_Name'
    title = 'Tiff_Title'
    sld.get_multiband_raster_sld(name, title=title)

    assert render.call_args[1]['title'] == title


def test_title_exists_in_template_params(render):
    # if title not passed in template_params
    # should have a title attr

    name = 'Some_Name'
    sld.get_multiband_raster_sld(name)

    assert 'title' in render.call_args[1]


def test_band_is_a_list_or_tuple():
    # If bands is not a list/tuple should
    # throw an exception

    name = 'Some_Name'
    bands = 'Wrong Band Type'

    with pytest.raises(AssertionError):
        sld.get_multiband_raster_sld(name, bands=bands)


def test_band_values_are_greater_than_zero():
    # If any value of bands is less than 1
    # should throw an exception

    name = 'Some_Name'
    bands = [1, 2, -1]

    with pytest.raises(AssertionError):
        sld.get_multiband_raster_sld(name, bands=bands)


def test_band_values_are_integers():
    # If any value of bands is not an
    # integer, should throw an exception

    name = 'Some_Name'
    bands = [1, 1.3, 2.0]

    with pytest.raises(AssertionError):
        sld.get_multiband_raster_sld(name, bands=bands)


def test_number_of_bands_are_correct(render):
    # If 3 bands are passed there must be 3 channels

    name = 'Some_Name'
    bands = (1, 2, 3)
    sld.get_multiband_raster_sld(name,
                                 bands=bands)
    num_of_bands = render.call_args[1]['channels']

    assert len(num_of_bands) == 3


def test_band_numbers_must_be_three():
    # Given number of bands must be equal to 3

    name = 'Some_Name'
    bands = [4, 5, 6, 9, 12]

    with pytest.raises(AssertionError):
        sld.get_multiband_raster_sld(name, bands=bands)


def test_given_band_values_are_set_correctly(render):
    # Given band order must match with channel's band properties

    name = 'Some_Name'
    bands = [9, 5, 2]
    sld.get_multiband_raster_sld(name,
                                 bands=bands)
    out_bands = [i['band'] for i in render.call_args[1]['channels']]

    assert bands == out_bands


def test_default_single_interval_is_applied_to_all_bands(render):
    # If interval is not passed in and bands=(1,2,3)
    # template_params['interval'] should equal [(0,1), (0,1), (0,1)]

    name = 'Some_Name'
    sld.get_multiband_raster_sld(name)
    intervals = [(i['options']['minValue'], i['options']['maxValue'])
                 for i in render.call_args[1]['channels']]

    assert intervals == [(0, 1), (0, 1), (0, 1)]


def test_given_single_interval_is_applied_to_all_bands(render):
    # If interval is passed in as tuple (10, 20) and bands=(1,2,3)
    # template_params['interval'] should equal [(10,20), (10,20), (10,20)]

    name = 'Some_Name'
    interval = (10, 20)
    sld.get_multiband_raster_sld(name,
                                 interval=interval)
    intervals = [(i['options']['minValue'], i['options']['maxValue'])
                 for i in render.call_args[1]['channels']]

    assert intervals == [(10, 20), (10, 20), (10, 20)]


def test_given_multi_interval_is_applied_correctly(render):
    # If interval is passed in as a list of tuples
    # [(10,20), (40,50), (90,100)] and bands=(1,2,3)
    # template_params['interval'] should equal
    # to [(10,20), (40,50), (90,100)]

    name = 'Some_Name'
    intervals = [(10, 20), (40, 50), (90, 100)]
    sld.get_multiband_raster_sld(name,
                                 interval=intervals)
    out_intervals = [(i['options']['minValue'], i['options']['maxValue'])
                     for i in render.call_args[1]['channels']]

    assert intervals == out_intervals


def test_number_of_intervals_is_equal_to_number_of_bands():
    # If interval is passed in as a list [(0,1),(0,1)] and
    # bands (1,2,3) should throw an exception """

    name = 'Some_Name'
    interval = [(0, 1), (1, 2)]

    with pytest.raises(AssertionError):
        sld.get_multiband_raster_sld(name, interval=interval)


def test_intervals_must_have_two_values():
    # If intervals has more or less then two
    # elements, should throw an exception

    name = 'Some_Name'
    intervals_1 = (0, 1, 2)
    intervals_2 = [(0, 1, 2), (0, 3, 4), (0)]

    with pytest.raises(AssertionError):
        sld.get_multiband_raster_sld(name, interval=intervals_1)

    with pytest.raises(AssertionError):
        sld.get_multiband_raster_sld(name, interval=intervals_2)


def test_gamma_is_a_number():
    # If gamma is not passed as a number thrown an
    # exception

    name = 'Some_Name'
    # Give a string with length of 3
    expected_gamma = 'Gam'

    with pytest.raises(AssertionError):
        sld.get_multiband_raster_sld(name, gamma=expected_gamma)


def test_number_of_gamma_is_equal_to_number_of_bands():
    # If gamma is passed in as list [0.1, 0.2] and bands (1,2,3)
    # should throw an exception

    name = 'Some_Name'
    gamma = [0.1, 0.2]

    with pytest.raises(AssertionError):
        sld.get_multiband_raster_sld(name, gamma=gamma)


def test_default_gamma_is_applied_to_all_bands(render):
    # If gamma is not passed in and bands=(1,2,3)
    # template_params['gamma'] should equal [(1.0), (1.0), (1.0)]

    name = 'Some_Name'
    sld.get_multiband_raster_sld(name)
    gamma = [i['options']['gamma'] for i in render.call_args[1]['channels']]

    assert gamma == [(1.0), (1.0), (1.0)]


def test_given_gamma_is_applied_to_all_bands(render):
    # If gamma is given 1.5 in and bands=(1,2,3)
    # template_params['gamma'] should equal [(1.5), (1.5), (1.5)]

    name = 'Some_Name'
    gamma = 1.5
    sld.get_multiband_raster_sld(name,
                                 gamma=gamma)
    gamma = [i['options']['gamma'] for i in render.call_args[1]['channels']]

    assert gamma == [(1.5), (1.5), (1.5)]


def test_given_multi_gamma_is_applied_correctly(render):
    # If gamma is given as list [1.0, 1.5, 2.0]
    # template_params['gamma'] should be equal to [1.0, 1.5, 2.0]

    name = 'Some_Name'
    gammas = [1.0, 1.5, 2.0]
    sld.get_multiband_raster_sld(name,
                                 gamma=gammas)
    gammas_out = [i['options']['gamma']
                  for i in render.call_args[1]['channels']]

    assert gammas_out == gammas


def test_opacity_is_a_number():
    # If opacity is not a number, should
    # throw an exception

    name = 'Some_Name'
    opacity = 'opacity'

    with pytest.raises(AssertionError):
        sld.get_multiband_raster_sld(name, opacity=opacity)


def test_opacity_is_between_0_and_1():
    # Opacity must be between 0 and 1

    name = 'Some_Name'
    opacity_1 = 1.5
    opacity_2 = -0.5

    with pytest.raises(AssertionError):
        sld.get_multiband_raster_sld(name, opacity=opacity_1)

    with pytest.raises(AssertionError):
        sld.get_multiband_raster_sld(name, opacity=opacity_2)


def test_default_opacity_is_applied_correctly(render):
    # If opacity is not provided it should default to 1.0

    name = 'Some_Name'
    sld.get_multiband_raster_sld(name)
    opacity = render.call_args[1]['opacity']

    assert opacity == 1.0


def test_opacity_is_applied_correctly(render):
    # If opacity is provided as 0.7 it should be equal to 0.7

    name = 'Some_Name'
    opacity = 0.7
    sld.get_multiband_raster_sld(name,
                                 opacity=opacity)
    opacity_out = render.call_args[1]['opacity']

    assert opacity_out == opacity


# TestSingleBandParams

def test_assigned_name_is_passed_correctly_single(render):
    # If name is given template_params['name'] should
    # be the same as the given name """

    name = 'Super Fancy Name'
    band = 1
    sld.get_single_band_raster_sld(name, band)

    assert render.call_args[1]['name'] == name


def test_deafault_title(render):
    # If title is None template_params['title']
    # should still be a string

    name = 'Some_Name'
    band = 1
    sld.get_single_band_raster_sld(name, band)

    assert type(render.call_args[1]['title']) == str


def test_band_is_greater_than_zero():
    # If band is less than 1
    # should throw an exception

    name = 'Some_Name'
    band = 0

    with pytest.raises(AssertionError):
        sld.get_single_band_raster_sld(name, band=band)


def test_given_band_value_is_set_correctly(render):
    # Given band must match with channel's band property

    name = 'Some_Name'
    band = 1
    sld.get_single_band_raster_sld(name, band)
    out_band = render.call_args[1]['channels'][0]['band']

    assert band == out_band


def test_name_exists_in_template_params(render):
    # Template params should have a name attribute

    name = 'Some_Name'
    band = 1
    sld.get_single_band_raster_sld(name, band)

    assert 'name' in render.call_args[1]


def test_title_exists_in_template_params_single(render):
    # Template params should have a title attribute

    name = 'Some_Name'
    band = 1
    sld.get_single_band_raster_sld(name, band)

    assert 'title' in render.call_args[1]


def test_opacity_exists_in_template_params(render):
    # Template params should have a opacity attribute

    name = 'Some_Name'
    band = 1
    sld.get_single_band_raster_sld(name, band)

    assert 'opacity' in render.call_args[1]


def test_channels_exists_in_template_params_single(render):
    # Template params should have a channels attribute

    name = 'Some_Name'
    band = 1
    sld.get_single_band_raster_sld(name, band)

    assert 'channels' in render.call_args[1]


def test_default_channel_name_is_passed_correctly(render):
    # if no custom channelName template_params['channels'][0]['name']
    # should be equal to GrayChannel

    name = 'Super Fancy Name'
    band = 1
    sld.get_single_band_raster_sld(name, band)

    assert render.call_args[1]['channels'][0]['name'] == 'GrayChannel'


def test_assigned_channel_name_is_passed_correctly(render):
    # If custom channelName template_params['channels'][0]['name']
    # should be equal to custom channelName

    name = 'Super Fancy Name'
    band = 1
    channel_name = "Super Channel Name"
    sld.get_single_band_raster_sld(name, band,
                                   channelName=channel_name)

    assert render.call_args[1]['channels'][0]['name'] == channel_name


def test_colormap_type_does_not_exist_in_template_params_by_default(render):
    # If no colormap_type is passed in no colormap_type
    # attr should be in template_params

    name = 'Some_Name'
    band = 1
    sld.get_single_band_raster_sld(name, band)

    assert 'colormap_type' not in render.call_args[1]


def test_colormap_type_assigned_correctly(render):
    # If custom colormap_type is passed in
    # template_params['colormap_type'] should be
    # equal to custom colormap_type

    name = 'Some_Name'
    band = 1
    colormap = [{"color": "#000000", "quantity": "0"},
                {"color": "#0000FF", "quantity": "1"}]
    colormap_type = "Different ramp"
    sld.get_single_band_raster_sld(name, band,
                                   colormap=colormap,
                                   colormap_type=colormap_type)

    assert colormap_type == render.call_args[1]['colormap_type']


def test_colormap_does_not_exist_in_template_params_by_default(render):
    # if colormap is None there should be no 'colormap'
    # attribute in template_params """

    name = 'Some_Name'
    band = 1
    sld.get_single_band_raster_sld(name, band)

    assert 'colormap' not in render.call_args[1]


def test_colormap_is_a_list_or_tuple():
    # If colormap is not a list/tuple should throw an exception

    name = 'Some_Name'
    band = 1
    colormap = "Not a List or Tuple"

    with pytest.raises(AssertionError):
        sld.get_single_band_raster_sld(name, band, colormap=colormap)


def test_colormap_is_a_collection_of_dictionaries():
    # If colormap values are not all dicts should throw an exception

    name = 'Some_Name'
    band = 1
    colormap = ["foo", "bar"]

    with pytest.raises(AssertionError):
        sld.get_single_band_raster_sld(name, band, colormap=colormap)


def test_each_colormap_element_has_color():
    # If colormap values do not all contain 'color'
    # attribute should thrown an exception

    name = 'Some_Name'
    band = 1
    colormap = [{'foo': 'bar'},
                {'bar': 'foo'}]

    with pytest.raises(AssertionError):
        sld.get_single_band_raster_sld(name, band, colormap=colormap)


def test_each_colormap_element_has_quantity():
    # If colormap values do not all contain 'quantity'
    # attribute should thrown an exception

    name = 'Some_Name'
    band = 1
    colormap = [{'foo': 'bar'},
                {'bar': 'foo'}]

    with pytest.raises(AssertionError):
        sld.get_single_band_raster_sld(name, band, colormap=colormap)


# TestXMLOutput

def test_given_band_values_are_set_correctly_xml():
    # Band Values should be set correctly

    name = 'Some_Name'
    expected_bands = [4, 3, 9]
    multiband_xml = sld.get_multiband_raster_sld(name,
                                                 bands=expected_bands)
    namespace = "{http://www.opengis.net/sld}"
    xml_bands = []
    root = ET.fromstring(multiband_xml.strip())
    for elem in root.iter("{}{}".format(namespace, 'SourceChannelName')):
        xml_bands.append(int(float(elem.text)))

    assert expected_bands == xml_bands


def test_given_band_value_is_set_correctly_xml():
    # Band Value should be set correctly

    name = 'Some_Name'
    expected_band = 2
    singleband_xml = sld.get_single_band_raster_sld(name,
                                                    band=expected_band)
    namespace = "{http://www.opengis.net/sld}"
    root = ET.fromstring(singleband_xml.strip())
    for elem in root.iter("{}{}".format(namespace, 'SourceChannelName')):
        assert int(float(elem.text)) == expected_band


def test_by_default_dont_have_colormap():
    # Call with no colormap should produce no ColorMap XML

    name = 'Some_Name'
    band = 2
    singleband_xml = sld.get_single_band_raster_sld(name, band)
    root = ET.fromstring(singleband_xml.strip())
    for elem in root.iter():
        if 'ColorMap' in elem.tag:
            colormap = elem
        else:
            colormap = False

    assert not colormap


def test_passed_colormap_exists_in_xml():
    # Call with colormap should produce ColorMap section

    name = 'Some_Name'
    band = 2
    colormap = [
        {"color": "#000000", "quantity": "100"},
        {"color": "#0000FF", "quantity": "110"},
        {"color": "#00FF00", "quantity": "135"},
        {"color": "#FF0000", "quantity": "160"},
        {"color": "#FF00FF", "quantity": "185"}]

    singleband_xml = sld.get_single_band_raster_sld(name, band,
                                                    colormap=colormap)
    root = ET.fromstring(singleband_xml.strip())
    for elem in root.iter():
        if 'ColorMap' in elem.tag:
            colormap = True
        else:
            colormap = False

    assert colormap


def test_number_of_color_entries_matches_xml():
    # Call with 4 colormap dicts should produce 4 ColorMap entries

    name = 'Some_Name'
    band = 2
    colormap = [
        {"color": "#000000", "quantity": "100"},
        {"color": "#0000FF", "quantity": "110"},
        {"color": "#00FF00", "quantity": "135"},
        {"color": "#FF00FF", "quantity": "185"}]

    singleband_xml = sld.get_single_band_raster_sld(name, band,
                                                    colormap=colormap)
    root = ET.fromstring(singleband_xml.strip())
    entries = []
    for elem in root.iter():
        if 'ColorMapEntry' in elem.tag:
            entries.append(elem)

    assert len(colormap) == len(entries)


def test_xml_items_have_quantity_and_color_attributes():
    # Call with colormap dicts that have 'color' and 'quantity'
    # should produce ColorMapEntry XML with 'color' and 'quantity' attributes

    name = 'Some_Name'
    band = 2
    colormap = [
        {"color": "#000000", "quantity": "100"},
        {"color": "#0000FF", "quantity": "110"},
        {"color": "#00FF00", "quantity": "135"},
        {"color": "#FF00FF", "quantity": "185"}]

    singleband_xml = sld.get_single_band_raster_sld(name, band,
                                                    colormap=colormap)
    root = ET.fromstring(singleband_xml.strip())

    for elem in root.iter():
        if 'ColorMapEntry' in elem.tag:
            if 'color' in elem.attrib and 'quantity' in elem.attrib:
                attrib = True
            else:
                attrib = False
            assert attrib
