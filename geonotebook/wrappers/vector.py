import collections

import fiona
import six

from ..shapes import shape


class VectorData(collections.Sequence):

    def __init__(self, path, **kwargs):
        if isinstance(path, six.string_types):
            self.reader = fiona.open(path)
        else:
            self.reader = path

    def __len__(self):
        return len(self.reader)

    def __getitem__(self, key):
        return self.reader[key]

    @property
    def shapes(self):
        """Return an iterator the generates shapes from geometries."""
        for feature in self.reader:
            yield shape(feature)

    @property
    def geojson(self):
        """Return an object (geojson) representation."""
        return {
            'type': 'FeatureCollection',
            'features': list(self.reader)
        }
