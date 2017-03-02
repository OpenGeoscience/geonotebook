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
        # fiona doesn't raise an error when accessing and invalid key
        if key < 0 or key >= len(self):
            raise IndexError()
        return self.reader[key]

    @property
    def geojson(self):
        """Return an object (geojson) representation."""
        features = list(self.reader)

        # Here, we add an id property to each feature which will
        # be used for styling on the client.
        for i, feature in enumerate(features):
            properties = feature.setdefault('properties', {})
            properties['_geonotebook_feature_id'] = i
        return {
            'type': 'FeatureCollection',
            'features': features
        }
