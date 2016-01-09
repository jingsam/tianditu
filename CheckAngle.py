# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

import os
import arcpy
from area import get_rings
from bearing import angle
from parallel import check_parallel


def check_mini_angle(args, cpus, pid):
    in_fc = args[0]
    tolerance = args[1]

    desc = arcpy.Describe(in_fc)
    errors = []

    cursor = arcpy.da.SearchCursor(in_fc, ["OID@", "SHAPE@"], spatial_reference=desc.spatialReference.GCS)
    for row in cursor:
        if row[0] % cpus != pid:
            continue

        rings = get_rings(row[1])
        for ring in rings:
            for i in xrange(0, len(ring) - 1):
                p1, p2, p3 = i, i + 1, i + 2
                if p3 == len(ring):
                    p3 = 1

                if ring[p1].X == ring[p2].X and ring[p1].Y == ring[p2].Y:
                    continue

                if ring[p2].X == ring[p3].X and ring[p2].Y == ring[p3].Y:
                    continue

                _angle = angle(ring[p1], ring[p2], ring[p3])

                if _angle <= tolerance:
                    errors.append('{0}, {1}, {2}, {3}, {4}\n'.format(row[0], 'ERR06', ring[p2].X, ring[p2].Y, _angle))
    del cursor

    return ''.join(errors)


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
    f.write('OID, ErrorID, X, Y, Angle\n')

    # result = check_mini_angle((in_fc, tolerance), 1, 0)
    result = check_parallel(check_mini_angle, (in_fc, tolerance))
    f.write(result)
    f.close()


if __name__ == "__main__":
    in_fc = arcpy.GetParameterAsText(0)
    tolerance = arcpy.GetParameterAsText(1)
    out_chk = arcpy.GetParameterAsText(2)

    check_angle(in_fc, float(tolerance), out_chk)