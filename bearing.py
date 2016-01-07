# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

from math import pi, sin, cos, atan2


def angle(point1, point2, point3):
    bearing21 = bearing(point2, point1)
    bearing23 = bearing(point2, point3)
    _angle = abs(bearing23 - bearing21)

    if _angle > 180:
        _angle = 360 -_angle

    return _angle


def bearing(point1, point2):
    lon1 = rad(point1.X)
    lat1 = rad(point1.Y)
    lon2 = rad(point2.X)
    lat2 = rad(point2.Y)

    a = sin(lon2 - lon1) * cos(lat2)
    b = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(lon2 - lon1)
    _bearing = degree(atan2(a, b))

    return _bearing


def rad(degree):
    return degree * pi / 180


def degree(rad):
    return rad * 180 / pi