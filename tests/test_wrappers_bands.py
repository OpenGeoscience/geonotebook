import unittest

# Band tests
## Mock out Band.reader
### test reader.get_band_data is called when get_data called
### test first argument to get_band_data is index that Band was initialized with
### test reader.get_band_min is called when min is accessed
### test first argument to get_band_min is index that Band was initialized with
### test reader.get_band_max is called when max is accessed
### test first argument to get_band_max is index that Band was initialized with
### test reader.get_band_mean is called when mean is accessed
### test first argument to get_band_mean is index that Band was initialized with
### test reader.get_band_stddev is called when stddev is accessed
### test first argument to get_band_stddev is index that Band was initialized with
### test reader.get_band_nodata is nodata when nodata is accessed
### test first argument to get_band_data is index that Band was initialized with

## Read in a test RasterData object (use geotiff for now)
### test get_data returns numpy array
### test get_data(masked=True) returns a numpy masked array
### test get_data has expected shape attribute
### test get_data(window=((0,0), (10, 10))) has a shape of (10, 10)
### test get_data(window=((0,0), (10, 20))) has a shape of (10, 20)
### test get_data(window=((0,0), (20, 10))) has a shape of (20, 10)



# BandCollection tests
## Read in a test RasterData object with multiple Bands (e.g. 4)
## descriptives (e.g. mean, min, max) for each band should be different

### BandCollection instantiated indexes other than list/tuple should throw an exception
### BandCollection instantiated with indexes where min is less than 1 should throw an exception
### BandCollection instantiated with indexes greater than 4 should throw an exception
### BandCollection instantiated with indexes == None should have length of 4
### length of bands should equal 4
### length of min should equal 4
### min values should equal known values
### length of max should equal 4
### max values should equal known values
### length of mean should equal 4
### mean values should equal known values
### length of stddev should equal 4
### stddev values should equal known values
### length of nodata should equal 4
### nodata values should equal known values
### get_data should return numpy array
### get_data should return numpy array of shape (X, Y, 4)
### get_data(mask=True) should return masked array
### test get_data(window=((0,0), (10, 10))) has a shape of (10, 10, 4)
### test get_data(window=((0,0), (10, 20))) has a shape of (10, 20, 4)
### test get_data(window=((0,0), (20, 10))) has a shape of (20, 10, 4)
### iterating through BandCollection should yield only objects of type BandCollection.band_class
### BandCollection[1] should return a BandObject
### BandCollection[[1,2,3]] should return a BandCollection
### BandCollection[[1,2,3]] should return a BandCollection of length 3
### BandCollection[0] should throw an Exception
### BandCollection[[0,1,2]] should throw an Exception
### BandCollection[[1, 1, 1]] should return a BandCollection of length 3
### BandCollection[[1, 1, 1]] should return a BandCollection where each Band has an index of 1
### BandCollection['foo'] should throw a KeyError

# RasterData
# RasterData.register('ext', testClass) should create an 'ext' key in RasterData._concrete_data_types
# if you RasterData.register('ext', testClass), RasterData._concrete_data_types['ext'] should give you testClass
# if you RasterData.register('ext', testClass) and create RasterData('foo.ext') then reader should by of type testClass
# RasterData.bands should return a BandCollection
# Mock reader, RasterData.count should call reader.count
# Mock reader, RasterData.path should call reader.path
# Mock index, RasterData.index should call reader.index
