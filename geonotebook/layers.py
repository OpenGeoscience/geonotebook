from config import Config
from collections import namedtuple
import rasterio
import annotations
import numpy as np

BBox = namedtuple('BBox', ['ulx', 'uly', 'lrx', 'lry'])

# Note:  GeonotebookLayers must support instances where data is
#        None. This allows us to use a consistent interface for things
#        like the OSM base layer,  or more generally for tile server URLs
#        that don't have any (accessible) data associated with them.



class GeonotebookLayer(object):
    def __init__(self, name, remote, **kwargs):
        self.config = Config()
        self.remote = remote
        self.name = name

    def __repr__(self):
        return "<{}('{}')>".format(
            self.__class__.__name__, self.name)


class AnnotationLayer(GeonotebookLayer):
    _annotation_types = {
        "point" : annotations.Point,
        "rectangle" : annotations.Rectangle,
        "polygon": annotations.Polygon
    }

    def __init__(self, name, remote, stack, **kwargs):
        super(AnnotationLayer, self).__init__(name, remote, **kwargs)
        self.stack = stack
        self.params = kwargs

        self._annotations = []

    def add_annotation(self, ann_type, coords, meta):
        self._annotations.append(
            self._annotation_types[ann_type](self, coords, **meta))

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

# GeonotebookStack supports dict-like indexing on a list
# of Geonotebook Layers. We could implement this with an
# OrderedDict,  but i think we are eventually going to want
# to support re-ordering,  potentially serializing etc so it
# Seems like putting it in its own class is best for now.

# TODO: support slices other list functionality etc
# TODO: convert to collections.mutablesequence
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

    def __len__(self):
        return len(self._layers)

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


    # TODO: this should really be stored with a reference
    #       in a private member variable
    @property
    def annotation(self):
        for l in self:
            if l.name == 'annotation':
                return l
        return None
