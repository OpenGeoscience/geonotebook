import collections
import functools

import fiona
from pyproj import Proj, transform
from shapely import geometry as shapely_geometry, ops
import six


class VectorData(collections.Sequence):

    def __init__(self, path, **kwargs):
        if isinstance(path, six.string_types):
            self.reader = fiona.open(path)
        else:
            self.reader = path

        self._transform = functools.partial(
            transform,
            Proj(**self.reader.crs),
            Proj(init='epsg:4326')
        )

    def __len__(self):
        return len(self.reader)

    def __getitem__(self, key):
        # fiona doesn't raise an error when accessing and invalid key
        if key < 0 or key >= len(self):
            raise IndexError()
        return self.reader[key]

    def _reproject(self, geometry):
        """Reproject a geojson-like geometry object."""
        shape = shapely_geometry.shape(geometry)
        reprojected = ops.transform(self._transform, shape)
        return shapely_geometry.geo.mapping(reprojected)

    @property
    def geojson(self):
        """Return an object (geojson) representation."""
        features = list(self.reader)

        # Here, we add an id property to each feature which will
        # be used for styling on the client.
        for i, feature in enumerate(features):
            properties = feature.setdefault('properties', {})
            properties['_geonotebook_feature_id'] = i
            feature['geometry'] = self._reproject(feature['geometry'])
        return {
            'type': 'FeatureCollection',
            'features': features
        }
