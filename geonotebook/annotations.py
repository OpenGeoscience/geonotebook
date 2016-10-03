class Annotation(object):
    def __init__(self, coordinates, **kwargs):
        self.coordinates = coordinates
        for k, v in kwargs.items():
            setattr(self, k, v)


class Point(Annotation):
    def __init__(self, coordinates, **kwargs):
        super(Point, self).__init__(coordinates, **kwargs)


class Rectangle(Annotation):
    def __init__(self, coordinates, **kwargs):
        super(Rectangle, self).__init__(coordinates, **kwargs)


class Polygon(Annotation):
    def __init__(self, coordinates, **kwargs):
        super(Polygon, self).__init__(coordinates, **kwargs)
