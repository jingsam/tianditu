# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'


from math import pi, sin, cos, atan2, sqrt


def line_distance(line):
    length = 0
    for segment in line:
        for i in xrange(0, len(segment) - 1):
            length += distance(segment[i], segment[i + 1])

    return length


def distance(point1, point2):
    dLat = rad(point2.X - point1.X)
    dLon = rad(point2.Y - point1.Y)
    lat1 = rad(point1.X)
    lat2 = rad(point2.X)

    a = pow(sin(dLat / 2), 2) + pow(sin(dLon/2), 2) * cos(lat1) * cos(lat2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return c * 6378137


def rad(degree):
    return degree * pi / 180