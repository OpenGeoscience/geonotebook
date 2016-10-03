from shapely.geometry import Point as sPoint
from shapely.geometry import Polygon as sPolygon

class Point(sPoint):
    def __init__(self, coordinates, **kwargs):

        for k, v in kwargs.items():
            setattr(self, k, v)

        super(Point, self).__init__(coordinates[0]['x'], coordinates[0]['y'])


class Rectangle(sPolygon):
    def __init__(self, coordinates, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

        super(Rectangle, self).__init__(
            [(c['x'], c['y']) for c in coordinates])


class Polygon(sPolygon):
    def __init__(self, coordinates, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

        super(Polygon, self).__init__(
            [(c['x'], c['y']) for c in coordinates])
