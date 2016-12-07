import collections

import geopandas
import six

from ..annotations import Point, Polygon


class VectorData(collections.Sequence):

    def __init__(self, path, **kwargs):
        if isinstance(path, six.string_types):
            self.reader = geopandas.read_file(path)
        elif isinstance(path, geopandas.GeoDataFrame):
            self.reader = path
        else:
            raise Exception('Unknown input type')

    def __len__(self):
        return len(self.reader)

    def __getitem__(self, keys):
        return self.reader.iloc[keys]

    @property
    def annotations(self):
        """Return an iterator the generates annotations from geometries."""
        for index, row in self.reader.iterrows():
            props = row.to_dict()
            geometry = props.pop('geometry')
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
        """Return a serialized (geojson) representation."""
        return self.reader.to_json()
