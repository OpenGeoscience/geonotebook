from config import Config
from collections import namedtuple
import annotations
from collections import OrderedDict

BBox = namedtuple('BBox', ['ulx', 'uly', 'lrx', 'lry'])


class GeonotebookLayer(object):
    # Control whether or not a layer can be modified
    # within a geonotebook stack or not. e.g. base OSM
    # map layer should not be deleted by the user
    _system_layer = False

    # _expose_as lets us control whether or not a layer is
    # directly exposed as an attribute on a geostack. It
    # is designed for layers added by the system that provide
    # some kind of functionality (e.g. the annotatoin layer).
    _expose_as = None

    def __init__(self, name, remote, **kwargs):
        self.config = Config()
        self.remote = remote
        self.name = name

        self._system_layer = kwargs.get("system_layer", False)
        self._expose_as = kwargs.get("expose_as", False)

    def __repr__(self):
        return "<{}('{}')>".format(
            self.__class__.__name__, self.name)


class AnnotationLayer(GeonotebookLayer):
    _annotation_types = {
        "point": annotations.Point,
        "rectangle": annotations.Rectangle,
        "polygon": annotations.Polygon
    }

    def __init__(self, name, remote, stack, **kwargs):
        super(AnnotationLayer, self).__init__(name, remote, **kwargs)
        self.stack = stack
        self.params = kwargs
        self._remote = remote
        self._annotations = []

    def add_annotation(self, ann_type, coords, meta):
        self._annotations.append(
            self._annotation_types[ann_type](self, coords, **meta))

    def clear_annotations(self):
        def _clear_annotations(num):
            self._annotations = []

        def rpc_error(error):
            self.log.error("JSONRPCError (%s): %s" % (error['code'], error['message']))

        return self._remote.clear_annotations().then(_clear_annotations, rpc_error)

    @property
    def points(self):
        return [a for a in self._annotations
                if type(a) == self._annotation_types['point']]

    @property
    def rectangles(self):
        return [a for a in self._annotations
                if type(a) == self._annotation_types['rectangle']]

    @property
    def polygons(self):
        return [a for a in self._annotations
                if type(a) == self._annotation_types['polygon']]


class NoDataLayer(GeonotebookLayer):
    def __init__(self, name, remote, vis_url, **kwargs):
        super(NoDataLayer, self).__init__(name, remote, **kwargs)
        self.vis_url = vis_url


class DataLayer(GeonotebookLayer):
    def __init__(self, name, remote, data, vis_url=None, **kwargs):
        super(DataLayer, self).__init__(name, remote, **kwargs)
        self.data = data

        # index into data in the form of ((ulx, uly), (lrx, lry))
        self._window = None

        assert vis_url is not None or data is not None, \
            "Must pass in vis_url or data to {}".format(
                self.__class__.__name__)

    @property
    def region(self):
        if self.data is None:
            return None

        if self._window is None:
            return self.data.get_data()
        else:
            return self.data.get_data(window=self._window)


    @region.setter
    def region(self, value):
        assert isinstance(value, BBox), \
            "Region must be set to a value of type BBox"

        if self.data is not None:
            self._window = self.data.index(value.ulx, value.uly), \
                self.data.index(value.lrx, value.lry)


class SimpleLayer(DataLayer):
    def __init__(self, name, remote, data, vis_url=None, **kwargs):
        super(SimpleLayer, self).__init__(name, remote, data, vis_url=vis_url, **kwargs)
        self.vis_url = vis_url

        if self.vis_url is None:
            self.vis_url = self.config.vis_server.ingest(
                self.data, name=self.name)

        self.params = self.config.vis_server.get_params(
            self.name, self.data, **kwargs)


class TimeSeriesLayer(DataLayer):
    def __init__(self, name, remote, data, vis_url=None, **kwargs):
        super(TimeSeriesLayer, self).__init__(name, remote, data, vis_url=None, **kwargs)
        self.__cur = 0
        self._remote = remote

        # TODO: check vis_url is valid length etc
        self._vis_url = vis_url if vis_url is not None else [None] * len(self.data)
        self._params = [None] * len(self.data)

        if self.vis_url is None:
            self.vis_url = self.config.vis_server.ingest(
                self.current, name=self.current.name)

        self.vis_server_kwargs = kwargs



    @property
    def params(self):
        if self._params[self._cur] is None:
            self._params[self._cur] = self.config.vis_server.get_params(
                self.current.name, self.current, **self.vis_server_kwargs)
        return self._params[self._cur]

    @property
    def vis_url(self):
        return self._vis_url[self._cur]

    @vis_url.setter
    def vis_url(self, value):
        self._vis_url[self._cur] = value

    @property
    def _cur(self):
        return self.__cur

    @_cur.setter
    def _cur(self, value):
        if value < 0:
            raise IndexError("No time slice at index {}!".format(value))

        if value >= len(self.data):
            raise IndexError("No time slice at index {}!".format(value))

        self.__cur = value

    @property
    def current(self):
        return self.data[self._cur]

    def _replace_layer(self):
        if self.vis_url is None:
            self.vis_url = self.config.vis_server.ingest(
                self.current, name=self.current.name)

        # TODO: Need better handlers here for post-replace callbacks
        self._remote.replace_wms_layer(self.name, self.vis_url, self.params)\
            .then(lambda resp: True, lambda: True)

        return self.current

    def seek(self, idx):
        self._cur = idx
        return self._replace_layer()

    def prev(self):
        self._cur -= 1
        return self._replace_layer()

    def next(self):
        try:
            self._cur += 1
            return self._replace_layer()
        except IndexError:
            raise StopIteration()


class GeonotebookStack(object):
    def __init__(self, layers=None):
        self._layers = OrderedDict()
        self._system_layers = OrderedDict()

        if layers is not None:
            for l in layers:
                self.append(l)

    def append(self, value):
        if isinstance(value, GeonotebookLayer):
            if value._system_layer:
                if value.name not in self._system_layers:
                    self._system_layers[value.name] = value
                else:
                    raise Exception("There is already a layer named %s" % value.name)
            else:
                if value.name not in self._layers:
                    self._layers[value.name] = value
                else:
                    raise Exception("There is already a layer named %s" % value.name)

            if value._expose_as is not None:
                self._expose_layer(value)

        else:
            raise Exception("Can only append GeonotebookLayers to Stack")

    def remove(self, value):
        if isinstance(value, basestring):
            del self._layers[value]
        elif isinstance(value, GeonotebookLayer):
            del self._layers[value.name]

    def find(self, predicate):
        """Find first GeonotebookLayer that matches predicate. If predicate
        is not callable it will check predicate against each layer name."""

        if not hasattr(predicate, '__call__'):
            try:
                return self._layers[predicate]
            except KeyError:
                return None

        try:
            # Note that we never find a system layer
            return next(l for l in self._layers if predicate(l))
        except StopIteration:
            return None

    def __getitem__(self, value):
        if isinstance(value, int):
            return [layer for name, layer in self._layers.items()][value]
        else:
            return self._layers.__getitem__(value)

    def __setitem__(self, index, value):
        if isinstance(value, GeonotebookLayer):
            if isinstance(index, int):
                self.__setitem__(
                    [name for name, layer in self._layers.items()][index],
                    value)
            else:
                self._layers.__setitem__(index, value)
        else:
            raise Exception("Can only add GeonotebookLayers to Stack")

    def __repr__(self):
        return "GeonotebookStack({})".format(
            [layer for _, layer in self._layers].__repr__())

    def __len__(self):
        return len(self._layers)

    def _expose_layer(self, layer):
        if layer._expose_as is not None:
            if not hasattr(self, layer._expose_as):
                setattr(self, layer._expose_as, layer)
            else:
                raise RuntimeError(
                    'Failed exposing "%s", attribute already exists' %
                    layer._expose_as)
