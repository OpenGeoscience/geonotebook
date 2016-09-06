import os
import numpy as np
import pkg_resources as pr
import collections

class Band(object):
    def __init__(self, index, data):
        self.data = data
        self.index = index

    def __repr__(self):
        return "<{}('{}')>".format(self.__class__.__name__,
                                   self.name)

    def get_data(self, window=None):
        if window is None:
            return self.reader.get_band_data(self.index)

        return self.reader.get_band_data(self.index, window=window)

    @property
    def min(self):
        return self.reader.get_band_min(self.index)

    @property
    def max(self):
        return self.reader.get_band_max(self.index)

    @property
    def mean(self):
        return self.reader.get_band_mean(self.index)

    @property
    def stddev(self):
        return self.reader.get_band_stddev(self.index)

    @property
    def name(self):
        return self.reader.get_band_name(self.index)

    @property
    def reader(self):
        return self.data.reader



class BandCollection(collections.Sequence):
    band_class = Band

    def __init__(self, data, indexes=None):
        self.data = data
        self.indexes = range(1, self.reader.count + 1) \
            if indexes is None else indexes

        assert not min(self.indexes) < 1, \
            IndexError("Bands are indexed from 1")

        assert not max(self.indexes) > self.reader.count, \
            IndexError("Band index out of range")

    @property
    def reader(self):
        return self.data.reader

    @property
    def min(self):
        return [self.band(i).min for i in self.indexes]

    @property
    def max(self):
        return [self.band(i).max for i in self.indexes]

    def band(self, index):
        return self.band_class(index, self.data)

    def get_data(self, window=None, axis=2):
        if len(self) == 1:
            return self.band(self.indexes[0]).get_data(window=window)
        else:
            return np.stack([self.band(i).get_data(window=window)
                             for i in self.indexes], axis=axis)

    def __iter__(self):
        for i in self.indexes:
            yield self.band(i)

    def __repr__(self):
        if self.reader.count > 6:
            return "<{}({})>".format(self.__class__.__name__,
                                     len(self.indexes))
        else:
            return "<{}({})>".format(self.__class__.__name__,
                                     len(self.indexes))

    def __len__(self):
        return len(self.indexes)

    def __getitem__(self, key):
        if isinstance(key, slice):
            idx = key.indices(len(self.indexes))
            return BandCollection(self.data, range(*idx))

        elif isinstance(key, (list, tuple)):
            return BandCollection(self.data, key)

        else:
            return self.band(key)


class RasterData(object):

    _concrete_data_types = {}

    @classmethod
    def register(cls, name, concrete_class):
        # TODO: some kind of validation on the API provided
        #       by the object from ep.load?
        cls._concrete_data_types[name] = concrete_class

    @classmethod
    def discover_concrete_types(cls):
        for ep in pr.iter_entry_points(group='geonotebook.wrappers.raster'):
            cls.register(ep.name, ep.load())

    def __init__(self, path, kind=None):
        if kind is None:
            # Get kind from the extension
            kind = os.path.splitext(path)[1][1:]

        try:
            self.reader = self._concrete_data_types[kind](path)
        except KeyError:
            raise NotImplementedError(
                "{} cannot parse files of type '{}'".format(
                    self.__class__.__name__, kind))

    def index(self, *args, **kwargs):
        return self.reader.index(*args, **kwargs)

    def read(self, *args, **kwargs):
        return self.reader.read(*args, **kwargs)

    @property
    def count(self):
        return self.reader.count

    @property
    def path(self):
        return self.reader.path

    @property
    def bands(self):
        return BandCollection(self)


RasterData.discover_concrete_types()
