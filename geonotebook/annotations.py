from shapely.geometry import Point as sPoint
from shapely.geometry import Polygon as sPolygon

from .shapes import wrap_shapely


class Annotation(object):
    def __init__(self, *args, **kwargs):
        self.layer = kwargs.pop('layer', None)
        self._metadata = kwargs
        for k, v in kwargs.items():
            setattr(Annotation, k, property(self._get_metadata(k),
                                            self._set_metadata(k),
                                            None))

        super(Annotation, self).__init__(*args)
        wrap_shapely(self)

    def _get_metadata(self, k):
        def _get_metadata(self):
            return self._metadata[k]
        return _get_metadata

    def _set_metadata(self, k):
        def _set_metadata(self, v):
            # TODO: these will have to communicate
            # updates to the clientside via self.layer._remote
            self._metadata[k] = v
        return _set_metadata

    def _get_layer_collection(self):
        return self.layer.layer_collection if self.layer is not None else []

    def get_data_window(self, minx, miny, maxx, maxy):
        return ((min(minx, maxx), min(miny, maxy)),
                (max(minx, maxx), max(miny, maxy)))

    @property
    def data(self):
        for layer in self._get_layer_collection():
            if hasattr(layer, "data") and layer.data is not None:
                yield layer, self.subset(layer.data, **self._metadata)


class Point(Annotation, sPoint):
    pass


class Rectangle(Annotation, sPolygon):
    pass


class Polygon(Annotation, sPolygon):
    pass
