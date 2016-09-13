import unittest

# GeonotebookStack
## Instantiate GeonotebookStack with list of non GeonotebookLayers should throw Exception

## Instantiate GeonotebookStack with list of GeonotebookLayers (e.g. 3 layers 'foo', 'bar', 'baz')
### GeonotebookStack.find('foo') should return GeonotebookLayer
### GeonotebookStack.find('derp') should return None
### GeonotebookStack.find(lambda g: g.name == 'foo') should return GeonotebookLayer
### GeonotebookStack.find(lambda g: g.name == 'derp') should return None
### GeonoteobokStack.indexOf('foo') should return 0
### GeonoteobokStack.indexOf('bar') should return 1
### GeonoteobokStack.indexOf('baz') should return 2
### GeonoteobokStack.indexOf('derp') should return None
### GeonotebookStack[0] should return GeonotebookLayer and name should equal 'foo'
### GeonotebookStack['foo'] should return GeonotebookLayer and name should equal 'foo'
