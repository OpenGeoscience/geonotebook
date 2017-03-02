import collections

import fiona
import six

from .. import annotations


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

    @property
    def points(self):
        """Return a generator of "Point" annotation objects."""
        for feature in self.reader:
            geometry = feature['geometry']
            if geometry['type'] == 'Point':
                coords = geometry['coordinates']
                yield annotations.Point(
                    coords, **feature['properties']
                )
            elif geometry['type'] == 'MultiPoint':
                for coords in geometry['coordinates']:
                    yield annotations.Point(
                        coords, **feature['properties']
                    )

    @property
    def polygons(self):
        """Return a generator of "Polygon" annotation objects."""
        for feature in self.reader:
            geometry = feature['geometry']
            if geometry['type'] == 'Polygon':
                coords = geometry['coordinates']
                yield annotations.Polygon(
                    coords[0], coords[1:], **feature['properties']
                )
            elif geometry['type'] == 'MultiPolygon':
                for coords in geometry['coordinates']:
                    yield annotations.Polygon(
                        coords[0], coords[1:], **feature['properties']
                    )
