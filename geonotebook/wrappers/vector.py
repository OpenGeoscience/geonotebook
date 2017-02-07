import collections

import geopandas
import six


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
    def geojson(self):
        """Return a serialized (geojson) representation."""
        return self.reader.to_json()
