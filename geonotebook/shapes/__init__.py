"""Export various objects representing shapes in geonotebook.

This module contains thin wrappers around shapely objects which provide
the ability to subset raster data objects via a ``subset`` member
function.
"""
from .point import Point
from .polygon import Polygon
from .rectangle import Rectangle

__all__ = ('Point', 'Polygon', 'Rectangle')
