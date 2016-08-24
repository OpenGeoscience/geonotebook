from config import Config

class GeonotebookLayer(object):
    def __init__(self, name, vis_url=None, data_path=None):
        self.config = Config()
        self.name = name

        assert vis_url is not None and data_path is not None, \
            "Must pass in vis_url or data_path to {}".format(
                self.__class__.__name__)

        if data_path is not None and vis_url is None:
            self.vis_url = self.config.vis_server.process(self.data_path)

        self.data_path = data_path

    def __repr__(self):
        return "<{}('{}')>".format(
            self.__class__.__name__, self.name)


# TODO: support slices other list functionality etc
class GeonotebookStack(object):
    def __init__(self, layers=None):
        if layers is not None:
            for l in layers:
                assert isinstance(l, GeonotebookLayer), \
                    "{} is not a GeonotebookLayer".format(l)
            self._layers = layers
        else:
            self._layers = []

    def __repr__(self):
        return "GeonotebookStack({})".format(self._layers.__repr__())

    def find(self, predicate):
        """Find first GeonotebookLayer that matches predicate. If predicate
        is not callable it will check predicate against each layer name."""

        if not hasattr(predicate, '__call__'):
            name = predicate
            predicate = lambda l: l.name == name

        try:
            return next(l for l in self._layers if predicate(l))
        except StopIteration:
            return None

    def indexOf(self, predicate):
        if not hasattr(predicate, '__call__'):
            name = predicate
            predicate = lambda l: l.name == name
        try:
            return next(i for i,l in enumerate(self._layers) if predicate(l))
        except StopIteration:
            return None


    def remove(self, value):
        if isinstance(value, basestring):
            idx = self.indexOf(value)
            if idx is not None:
                return self.remove(idx)
            else:
                raise KeyError('{}'.format(value))
        else:
            del self._layers[value]

    def append(self, value):
        if isinstance(value, GeonotebookLayer):
            if self.find(value.name) is None:
                self._layers.append(value)
            else:
                raise Exception("There is already a layer named {}".format(value.name))

        else:
            raise Exception("Can only append GeonotebookLayer to Stack")

    def __getitem__(self, value):
        if isinstance(value, basestring):
            idx = self.indexOf(value)
            if idx is not None:
                return self.__getitem__(idx)
            else:
                raise KeyError('{}'.format(value))
        else:
            return self._layers.__getitem__(value)

    def __setitem__(self, index, value):
        if isinstance(value, GeonotebookLayer):
            if isinstance(index, basestring):
                idx = self.indexOf(index)
                if idx is not None:
                    self.__setitem__(idx, value)
                else:
                    raise KeyError('{}'.format(value.name))
            else:
                self._layers.__setitem__(index, value)
        else:
            raise Exception("Can only append GeonotebookLayer to Stack")
