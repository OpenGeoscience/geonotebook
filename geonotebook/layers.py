from collections import namedtuple
from collections import OrderedDict
import sys
import six
import copy

from . import annotations
from .config import Config
from .vis.utils import generate_colormap

BBox = namedtuple('BBox', ['ulx', 'uly', 'lrx', 'lry'])


class VisOptions(object):
    def __init__(self, data, opacity=1.0, gamma=1.0, projection='EPSG:3857',
                 kernel_id=None, zIndex=None, colormap=None, interval=None,
                 layer_type=None, **kwargs):

        # self.vis_url = vis_url
        self.opacity = opacity
        self.projection = projection
        self.gamma = gamma
        self.interval = interval
        self.colormap = None
        self.zIndex = zIndex
        self.kernel_id = kernel_id
        self.layer_type = layer_type

        if data is not None and len(data.band_indexes) == 1:
            try:
                # If we have the colormap in the form
                # of a list of dicts with color/quantity then
                # set options['colormap'] equal to this
                for d in colormap:
                    assert 'color' in d
                    assert 'quantity' in d

                self.colormap = colormap

            except Exception:
                # Otherwise try to figure out the correct colormap
                # using data min/max
                try:
                    _min, _max = interval
                except TypeError:
                    _min, _max = None, None

                if _min is None:
                    try:
                        _min = min(data.min)
                    except (ValueError, TypeError):
                        _min = data.min

                if _max is None:
                    try:
                        _max = max(data.max)
                    except (ValueError, TypeError):
                        _max = data.max

                self.colormap = generate_colormap(
                    colormap, _min, _max)
        else:
            self.colormap = []

    def serialize(self):
        return {
            'layer_type': self.layer_type,
            'opacity': self.opacity,
            'gamma': self.gamma,
            'projection': self.projection,
            'interval': self.interval,
            'colormap': self.colormap,
            'kernel_id': self.kernel_id,
            'zIndex': self.zIndex
        }

    def __hash__(self):
        return hash((
            self.layer_type,
            self.opacity,
            self.gamma,
            self.interval,
            self.projection,
            tuple(tuple(c.items()) for c in self.colormap),
            self.kernel_id,
            self.zIndex))


class GeonotebookLayer(object):
    # Control whether or not a layer can be modified
    # within a geonotebook layer collection or not. e.g. base OSM
    # map layer should not be deleted by the user
    _system_layer = False

    # _expose_as lets us control whether or not a layer is
    # directly exposed as an attribute on a layer collection. It
    # is designed for layers added by the system that provide
    # some kind of functionality (e.g. the annotatoin layer).
    _expose_as = None

    def __init__(self, name, remote, data, **kwargs):
        self.config = Config()
        self.remote = remote
        self._name = name

        self._system_layer = kwargs.pop("system_layer", False)
        self._expose_as = kwargs.pop("expose_as", None)

        self.vis_options = VisOptions(data, **kwargs)

    def __repr__(self):
        return "<{}('{}')>".format(
            self.__class__.__name__, self.name)

    def serialize(self):
        return {
            'name': self.name,
            'vis_url': self.vis_url if hasattr(self, 'vis_url') else None,
            'vis_options': self.vis_options.serialize(),
            'query_params': self.query_params
        }

    @property
    def name(self):
        return self._name

    @property
    def query_params(self):
        return {}


class AnnotationLayer(GeonotebookLayer):
    _annotation_types = {
        "point": annotations.Point,
        "rectangle": annotations.Rectangle,
        "polygon": annotations.Polygon
    }

    def serialize(self):
        ret = super(AnnotationLayer, self).serialize()

        ret.update({
            'annotations': [annot.serialize() for annot in self._annotations]
        })

        return ret

    def __init__(self, name, remote, layer_collection, **kwargs):

        kwargs['layer_type'] = 'annotation'

        super(AnnotationLayer, self).__init__(name, remote, None, **kwargs)
        self.layer_collection = layer_collection
        self._remote = remote
        self.vis_url = None
        self._annotations = []

    def add_annotation(self, ann_type, coords, meta):
        if ann_type == 'point':
            x, y = coords[0]['x'], coords[0]['y']

            meta['layer'] = self

            self._annotations.append(
                self._annotation_types[ann_type](x, y, **meta))
        elif ann_type in self._annotation_types.keys():
            coordinates = [(c['x'], c['y']) for c in coords]

            meta['layer'] = self

            holes = meta.pop('holes', None)

            self._annotations.append(
                self._annotation_types[ann_type](coordinates, holes, **meta))
        else:
            raise RuntimeError("Cannot add annotation of type %s" % ann_type)

    def clear_annotations(self):
        # clear_annotations on _remote returns the
        # number of annotations that were cleared.
        # this isn't currently used inside the callback
        # but that is the signature of the function.
        def _clear_annotations(num):
            self._annotations = []

        def rpc_error(error):
            self.log.error(
                "JSONRPCError (%s): %s" % (error['code'], error['message'])
            )

        def callback_error(exception):
            self.log.error("Callback Error: %s" % exception[0])

        return self._remote.clear_annotations().then(
            _clear_annotations, rpc_error
        ).catch(callback_error)

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
        super(NoDataLayer, self).__init__(name, remote, None, **kwargs)
        self.vis_url = vis_url


class DataLayer(GeonotebookLayer):
    def __init__(self, name, remote, data=None, vis_url=None, **kwargs):
        super(DataLayer, self).__init__(name, remote, data, **kwargs)
        self.data = data

        assert vis_url is not None or data is not None, \
            "Must pass in vis_url or data to {}".format(
                self.__class__.__name__)


class SimpleLayer(DataLayer):
    def __init__(self, name, remote, data, vis_url=None, **kwargs):
        super(SimpleLayer, self).__init__(
            name, remote, data=data, vis_url=vis_url, **kwargs
        )

        if vis_url is None:
            self.vis_url = self.config.vis_server.ingest(
                self.data, name=self.name, **self.vis_options.serialize())

    @property
    def name(self):
        return "{}_{}".format(self._name, hash(self.vis_options) + sys.maxsize + 1)

    @property
    def query_params(self):
        return self.config.vis_server.get_params(
            self.name, self.data, **self.vis_options.serialize())



class TimeSeriesLayer(DataLayer):
    def __init__(self, name, remote, data, vis_url=None, **kwargs):
        super(TimeSeriesLayer, self).__init__(
            name, remote, data=data, vis_url=None, **kwargs
        )
        self.__cur = 0
        self._vis_urls = []

        self._remote = remote

        if vis_url is None:

            vis_url = self.config.vis_server.ingest(
                self.current, name=self.name, **self.vis_options.serialize())

            self._vis_options.append(vis_url)

    @property
    def vis_url(self):
        return self._vis_urls[self._cur]

    @property
    def name(self):
        _, options = self._vis_options[self._cur]
        return "{}_{}_{}".format(
            self._name, self.current.name, hash(options) + sys.maxsize + 1)


    @property
    def query_params(self):
        self.config.vis_server.get_params(
            self.current.name, self.current, **self.vis_options.serialize())


    @property
    def current(self):
        return self.data[self._cur]

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

    def _replace_layer(self):
        if self._cur > len(self._vis_options):
            vis_url = self.config.vis_server.ingest(
                self.current, name=self.current.name,
                **self.vis_options.serialize())

            self._vis_options.append(vis_url)

        self._remote.replace_layer(
            self._type, self.name, self.query_params) \
            .then(lambda resp: True, lambda: True)

        return self.current

    def idx(self, idx=None):
        if idx is None:
            return self._cur
        else:
            self._cur = idx
            return self._replace_layer()

    def backward(self):
        self._cur -= 1
        return self._replace_layer()

    def forward(self):
        self._cur += 1
        return self._replace_layer()


class GeonotebookLayerCollection(object):
    def __init__(self, layers=None):
        self._layers = OrderedDict()
        self._system_layers = OrderedDict()

        if layers is not None:
            for l in layers:
                self.append(l)

    # serialize functions must return a json-serializable data structure
    def serialize(self, include_system_layers=True):
        ret = {'layers': [],
               'system_layers': []}

        for name, layer in six.iteritems(self._layers):
            if hasattr(layer, 'serialize') and callable(layer.serialize):
                ret['layers'].append(layer.serialize())

        if include_system_layers:
            for name, layer in six.iteritems(self._system_layers):
                if hasattr(layer, 'serialize') and callable(layer.serialize):
                    ret['system_layers'].append(layer.serialize())

        return ret

    def append(self, value):
        if isinstance(value, GeonotebookLayer):
            if value._system_layer:
                if value.name not in self._system_layers:
                    self._system_layers[value.name] = value
                else:
                    raise Exception(
                        "There is already a layer named %s" % value.name
                    )
            else:
                if value.name not in self._layers:
                    self._layers[value.name] = value
                else:
                    raise Exception(
                        "There is already a layer named %s" % value.name
                    )

            if value._expose_as is not None:
                self._expose_layer(value)

        else:
            raise Exception("Can only append GeonotebookLayers to Collection")

    def remove(self, value):
        if isinstance(value, six.string_types):
            del self._layers[value]
        elif isinstance(value, GeonotebookLayer):
            del self._layers[value.name]

    def find(self, predicate):
        """Find first GeonotebookLayer that matches predicate.

        If predicate is not callable, it will check predicate against each
        layer name.
        """
        if not hasattr(predicate, '__call__'):
            try:
                return self._layers[predicate]
            except KeyError:
                return None

        try:
            # Note that we never find a system layer
            return next(l for l in self._layers.values() if predicate(l))
        except StopIteration:
            return None

    def __getitem__(self, value):
        if isinstance(value, six.integer_types):
            return [
                layer for name, layer in six.iteritems(self._layers)
            ][value]
        else:
            return self._layers.__getitem__(value)

    def __setitem__(self, index, value):
        if isinstance(value, GeonotebookLayer):
            if value._system_layer:
                raise Exception("Cannot add a system layer via __setitem__")

            if isinstance(index, six.integer_types):
                self.__setitem__(
                    [
                        name for name, layer in six.iteritems(self._layers)
                    ][index],
                    value)
            else:
                self._layers.__setitem__(index, value)
        else:
            raise Exception("Can only add GeonotebookLayers to Collection")

    def __repr__(self):
        return "<GeonotebookLayerCollection({})>".format(
            ([layer for layer in self._layers.values()]).__repr__())

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
