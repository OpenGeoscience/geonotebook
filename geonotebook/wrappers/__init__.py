import os
import numpy as np
import pkg_resources as pr
import collections

class RasterData(collections.Sequence):

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

    @classmethod
    def is_valid(cls, path):
        try:
            f = open(path, "r")
        except OSError:
            return False
        finally:
            f.close()

        kind = os.path.splitext(path)[1][1:]

        return kind in cls._concrete_data_types.keys()


    def __init__(self, path, kind=None, indexes=None):
        if kind is None:
            # Get kind from the extension
            kind = os.path.splitext(path)[1][1:]

        try:
            self.reader = self._concrete_data_types[kind](path)
        except KeyError:
            raise NotImplementedError(
                "{} cannot parse files of type '{}'".format(
                    self.__class__.__name__, kind))

        self.band_indexes = range(1, self.reader.count + 1) \
            if indexes is None else indexes

        assert not min(self.band_indexes) < 1, \
            IndexError("Bands are indexed from 1")

        assert not max(self.band_indexes) > self.reader.count, \
            IndexError("Band index out of range")


    def index(self, *args, **kwargs):
        return self.reader.index(*args, **kwargs)


    def get_data(self, window=None, masked=True, axis=2, **kwargs):
        if len(self) == 1:
            return self.reader.get_band_data(self.band_indexes[0],
                                             window=window,
                                             maksed=masked,
                                             **kwargs)
        else:
            if masked:
                # TODO: fix masked array hack here
                # Note that this also assumes nodata for first band is the
                # same for all other bands.  all around kind of a hack
                kwargs["masked"] = False
                return np.ma.masked_values(
                    np.stack([self.reader.get_band_data(i, window=window, **kwargs)
                              for i in self.band_indexes], axis=axis), self.nodata[0])
            else:
                return np.stack([self.reader.get_band_data(i, window=window,
                                                           masked=masked,
                                                           **kwargs)
                                 for i in self.band_indexes], axis=axis)

    def __len__(self):
        return len(self.band_indexes)

    def __getitem__(self, key):
        if isinstance(key, (list, tuple)):
            return RasterData(self.path, indexes=key)
        elif isinstance(key, int):
            return RasterData(self.path, indexes=[key])
        else:
            raise IndexError("Bands may only be indexed by int or list of ints")


    @property
    def min(self):
        if len(self) == 1:
            return self.reader.get_band_min(self.band_indexes[0])
        else:
            return [self.reader.get_band_min(i) for i in self.band_indexes]

    @property
    def max(self):
        if len(self) == 1:
            return self.reader.get_band_max(self.band_indexes[0])
        else:
            return [self.reader.get_band_max(i) for i in self.band_indexes]

    @property
    def mean(self):
        if len(self) == 1:
            return self.reader.get_band_mean(self.band_indexes[0])
        else:
            return [self.reader.get_band_mean(i) for i in self.band_indexes]

    @property
    def stddev(self):
        if len(self) == 1:
            return self.reader.get_band_stddev(self.band_indexes[0])
        else:
            return [self.reader.get_band_stddev(i) for i in self.band_indexes]

    @property
    def nodata(self):
        if len(self) == 1:
            return self.reader.get_band_nodata(self.band_indexes[0])
        else:
            return [self.reader.get_band_nodata(i) for i in self.band_indexes]

    @property
    def count(self):
        return self.reader.count

    @property
    def path(self):
        return self.reader.path

    @property
    def name(self):
        return os.path.splitext(os.path.basename(self.path))[0]


RasterData.discover_concrete_types()


class RasterDataCollection(collections.Sequence):
    def __init__(self, items, verify=True, indexes=None):

        if verify:
            assert len(set([RasterData(i).count for i in items])) == 1, \
                "Not all items have the same number of bands!"

        self._items = items

        # All band counts will be the same unless verify=False
        # in which case you've made your own bed.
        band_count = RasterData(self._items[0]).count

        self.band_indexes = range(1, band_count + 1) if indexes is None else indexes

        assert not min(self.band_indexes) < 1, \
            IndexError("Bands are indexed from 1")

        assert not max(self.band_indexes) > band_count, \
            IndexError("Band index out of range")

    def __iter__(self):
        for i in self._items:
            yield RasterData(i, indexes=self.band_indexes)

    def __len__(self):
        return len(self._items)

    def __getitem__(self, args):
        try:
            key, bands = args[0], args[1]
        except (KeyError, TypeError, IndexError):
            key, bands = args, None

        if isinstance(bands, int):
            bands = [bands]

        if isinstance(key, slice):
            idx = key.indices(len(self._items))
            return RasterDataCollection([self._items[i] for i in range(*idx)],
                                        indexes=self.band_indexes if bands is None else bands,
                                        verify=False)
        elif isinstance(key, int):
            return RasterData(self._items[key],
                              indexes=self.band_indexes if bands is None else bands)
        else:
            raise IndexError("{} must be of type slice, or int")


    def get_data(self, *args, **kwargs):
        raise NotImplementedError("get_data(...) Not implemented yet")

    def index(self, *args, **kwargs):
        raise NotImplementedError("index(...) Not implemented yet")


###### DELETE EVERYTHING AFTER ME ##########

DATA_DIR="/data/kotfic/NEX/golden_tile_layer/WELD/golden_tiles/geotiff/NBAR/"
def sort_NBAR(a, b):
  am, ay = int(a.split(".")[2][-2:]), int(a.split(".")[3])
  bm, by = int(b.split(".")[2][-2:]), int(b.split(".")[3])

  if ay < by:
    return -1
  elif ay > by:
    return 1
  elif by == ay:
    if am < bm:
      return -1
    elif am > bm:
      return 1
    else:
      return 0


PATHS = [DATA_DIR + p for p in sorted(os.listdir(DATA_DIR), sort_NBAR)]

if __name__ == "__main__":
    rdc = RasterDataCollection(PATHS)
