import os
import pkg_resources as pr

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

RasterData.discover_concrete_types()
