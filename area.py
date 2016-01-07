# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

from math import sin
from math import cos
from math import pi


def get_rings(polygon):
    rings = []
    for part in polygon:
        ring = []
        for point in part:
            if point:
                ring.append(point)
            else:
                rings.append(ring)
                ring = []
        if ring:
            rings.append(ring)

    return rings


def polygon_area(rings):
    area = 0
    if rings:
        for i in xrange(0, len(rings)):
            area += ring_area(rings[i])

    return area


def ring_area(ring):
    area = 0
    for i in xrange(0, len(ring) - 1):
        area += trapezoid_area(ring[i], ring[i + 1])

    return area


def trapezoid_area(point1, point2):
    lon1 = rad(point1.X)
    lat1 = rad(point1.Y)
    lon2 = rad(point2.X)
    lat2 = rad(point2.Y)

    if lat1 == lat2:
        return 0.0

    b2 = 4.04082999833e+13
    A = 1.00336408983
    B = 0.00112418938193
    C = 1.69945947352e-06
    D = 2.71785784558e-09
    E = 4.35841900483e-12

    dB = lat2 - lat1
    dL = (lon1 + lon2) / 2
    Bm = (lat1 + lat2) / 2

    sA = A * sin(0.5 * dB) * cos(Bm)
    sB = B * sin(1.5 * dB) * cos(3 * Bm)
    sC = C * sin(2.5 * dB) * cos(5 * Bm)
    sD = D * sin(3.5 * dB) * cos(7 * Bm)
    sE = E * sin(4.5 * dB) * cos(9 * Bm)
    S = 2 * b2 * dL * (sA - sB + sC - sD + sE)

    return -S


def ring_area2(ring):
    area = 0
    length = len(ring)

    if length > 2:
        p1, p2, p3 = 0, 0, 0
        for i in xrange(0, length - 1):
            if i == length - 2:
                p1, p2, p3 = length - 2, length - 1, 1
            else:
                p1, p2, p3 = i, i + 1, i + 2
            area += (rad(ring[p3].X) - rad(ring[p1].X)) * sin(ring[p2].Y)

    return area * 6378137 * 6378137 / 2


def rad(degree):
    return degree * pi / 180



