import unittest


# Testing argument mangling
## These mock out template.render and test directly against the template_params dict that is generated
## Multiband

### if title is None template_params['title'] should still be a string
### if title is passed in template_params['title'] should equal that string
### if bands is not a list/tuple should throw an exception
### if any value of bands is less than 1 should throw an exception
### if range is passed in as tuple (0,1) and bands=(1,2,3) template_params['range'] should equal [(0,1), (0,1), (0,1)]
### if range is passed in as list [(0,1), (0,1)] and bands = (1,2,3) should throw exception
### if gamma is passed in as 0.1 and bands=(1,2,3) template_params['bands'] should equal [0.1]
### if gamma is passed in as list [0.1, 0.2] and bands = (1,2,3) should throw exception
### template_params should have a name attr
### if title not passed in template_params should have a title attr
### if opacity not passed in template_params should have an opacity attr
### template_params should have a channels attr
### if 3 bands are passed in then len(template_params['channels']) should be 3
### if 4 bands are passed in then len(template_params['channels']) should be 3
### if 4 bands are passed in and 4 channelNames are passed in then len(template_params['chanenls']) should be 4
### if range is passed in as (0, 1) then each template_params['channels'][:]['options']['min'] should be 0
### if range is passed in as (0, 1) then each template_params['channels'][:]['options']['max'] should be 1
### if range is passed in as [(0, 1), (2, 3), (3, 4)] then each template_params['channels'][:]['options']['min'] should be [0, 2, 3] respectively
### if range is passed in as [(0, 1), (2, 3), (3, 4)] then each template_params['channels'][:]['options']['max'] should be [1, 3, 4] respectively
### if gamma is passed in as 0.5 then each template_params['channels'][:]['options']['gamma'] should be 0.5
### if gamma is passed in as [0.1, 0.5, 1] then each template_params['channels'][:]['options']['gamma'] should be [0.1, 0.5, 1] respectively
### if bands is (4, 5, 6) then template_params['channels'][:]['bands'] should be [4, 5, 6] respectively
### if custom channelNames is set up then template_params['channels'][:]['name'] should be equal to the channelNames


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



# Testing xml output
## These should be tested by importing the templates and passing dict values directly into template.render
## Multiband

### Call with three channels elements should produce three sections in ChannelSelection XML
### Call with one channel should produce one section in ChannelSelection XML
### Call with no colormap should produce no ColorMap XML
### Call with colormap should produce ColorMap section
### Call with 4 colormap dicts should produce 4 ColorMap entries
### Call with colormap dicts that have 'color' and 'quantity' should produce ColorMapEntry XML with 'color' and 'quantity' attributes
