import collections

import fiona
import six


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
    def geojson(self):
        """Return an object (geojson) representation."""
        return {
            'type': 'FeatureCollection',
            'features': list(self.reader)
        }
