from shapely.geometry import Polygon as sPolygon


class Rectangle(sPolygon):
    def subset(self, raster_data, **kwargs):
        ul = raster_data.index(self.bounds[0], self.bounds[1])
        lr = raster_data.index(self.bounds[2], self.bounds[3])
        window = self.get_data_window(ul[0], ul[1], lr[0], lr[1])

        # TODO: Trim window to valid range for raster data if out of bounds

        return raster_data.get_data(window=window, **kwargs)
