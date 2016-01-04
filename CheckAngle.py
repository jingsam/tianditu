# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

import os
import arcpy
from area import get_rings


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
    f.write('OID, ErrorID, X, Y, distance\n')

    errors = []
    cursor = arcpy.da.SearchCursor(in_fc, ["OID@", "SHAPE@",], spatial_reference=desc.spatialReference.GCS)
    for row in cursor:
        rings = get_rings(row[1])
        for ring in rings:
            for i in xrange(0, len(ring) - 1):
                p1, p3, p4 = i, i + 2, i + 3
                if p1 == len(ring) - 3:
                    p4 = 1
                elif p1 == len(ring) - 2:
                    p3, p4 = 1, 2

                point1 = arcpy.PointGeometry(ring[p1], desc.spatialReference.GCS)
                point3 = arcpy.PointGeometry(ring[p3], desc.spatialReference.GCS)
                point4 = arcpy.PointGeometry(ring[p4], desc.spatialReference.GCS)

                p1_p3 = point1.angleAndDistanceTo(point3)[1]
                p1_p4 = point1.angleAndDistanceTo(point4)[1]
                dist = min(p1_p3, p1_p4)

                if dist <= tolerance:
                    errors.append('{0}, {1}, {2}, {3}, {4}\n'.format(row[0], 'ERR06', ring[i].X, ring[i].Y, dist))
    del cursor

    f.write(''.join(errors))
    f.close()


if __name__ == "__main__":
    in_fc = arcpy.GetParameterAsText(0)
    tolerance = arcpy.GetParameterAsText(1)
    out_chk = arcpy.GetParameterAsText(2)

    check_angle(in_fc, float(tolerance), out_chk)