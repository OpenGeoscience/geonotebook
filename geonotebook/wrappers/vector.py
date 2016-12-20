import collections

import fiona
import six

from ..annotations import Point, Polygon


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
    def annotations(self):
        """Return an iterator the generates annotations from geometries."""
        for index, feature in enumerate(self.reader):
            props = feature['properties']
            geometry = feature['geometry']
            if geometry.geom_type == 'Point':
                yield Point(geometry, **props)
            elif geometry.geom_type == 'Polygon':
                yield Polygon(geometry, **props)
            elif geometry.geom_type == 'MultiPoint':
                for point in geometry.geoms:
                    yield Point(point, **props)
            elif geometry.geom_type == 'MultiPolygon':
                for polygon in geometry.geoms:
                    yield Polygon(polygon, **props)

    @property
    def geojson(self):
        """Return an object (geojson) representation."""
        return {
            'type': 'FeatureCollection',
            'features': list(self.reader)
        }
