# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

import os
from math import pi
import arcpy


def calc_angle(point1, point2, point3, sr):
    a = (point2.X - point1.X, point2.Y - point1.Y)
    b = (point3.X - point2.X, point3.Y - point2.Y)

    ab = a[0] * b[0] + a[1] * b[1]
    al = arcpy.Polyline([[point1.X, point1.Y], [point2.X, point2.Y]], sr)
    bl = arcpy.Polyline([[point2.X, point2.Y], [point3.X, point3.Y]], sr)
    a_b = ((a[0] ** 2 + a[1] ** 2) ** 0.5) * ((b[0] ** 2 + b[1] ** 2) ** 0.5)
    if a_b == 0:
        return 180

    return 180 - abs(ab) / a_b * 180 / pi


def check_angle(in_fc, tolerance, out_chk):
    if not arcpy.Exists(in_fc):
        arcpy.AddIDMessage("ERROR", 110, in_fc)
        raise SystemExit()

    desc = arcpy.Describe(in_fc)
    if desc.shapeType.lower() != "polygon":
        arcpy.AddIDMessage("ERROR", 931)
        raise SystemExit()

    if desc.spatialReference.name == "Unknown":
        arcpy.AddIDMessage("ERROR", 1024)
        raise SystemExit()

    ext = os.path.splitext(out_chk)[1]
    if ext != '.csv':
        out_chk += '.csv'
    f = open(out_chk, 'w')
    f.write('OID, ErrorID, X, Y\n')

    cursor = arcpy.da.SearchCursor(in_fc, ["SHAPE@", "OID@"], spatial_reference=desc.spatialReference.GCS)
    for row in cursor:
        for part in row[0]:
            for i in xrange(0, len(part) - 1):
                p1, p2, p3 = i - 1, i, i + 1
                if i == 0:
                    p1 = len(part) - 2

                angle = calc_angle(part[p1], part[p2], part[p3], desc.spatialReference.GCS)
                if angle <= tolerance:
                    f.write('{0}, {1}, {2}, {3}, {4}\n'.format(row[1], 'ERR06', part[p2].X, part[p2].Y, angle))
    del cursor
    f.close()


if __name__ == "__main__":
    in_fc = arcpy.GetParameterAsText(0)
    tolerance = arcpy.GetParameterAsText(1)
    out_chk = arcpy.GetParameterAsText(2)

    check_angle(in_fc, float(tolerance), out_chk)