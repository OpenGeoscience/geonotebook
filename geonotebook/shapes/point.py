from shapely.geometry import Point as sPoint


class Point(sPoint):
    def subset(self, raster_data, **kwargs):
        return raster_data.ix(self.x, self.y)
