# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

import os
import arcpy
from area import get_rings
from bearing import bearing, angle
from parallel import check_parallel


def check_mini_edge(in_fc, tolerance, cpus, pid):
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

                _bearing = bearing(ring[p1], ring[p2])
                _angle = angle(ring[p1], ring[p2], ring[p3])

                min_bearing = min(abs(_bearing), abs(_bearing - 90), abs(_bearing + 90), abs(_bearing - 180), abs(_bearing + 180))
                min_angle = min(abs(45 - _angle), abs(135 - _angle))

                p = p1 if _bearing >= 0 else p2
                if min_bearing <= tolerance[0] and min_angle <= tolerance[1]:
                    errors.append('{0}, {1}, {2}, {3}, {4}, {5}\n'.format(row[0], 'ERR07', ring[p].X, ring[p].Y, _bearing, _angle))
    del cursor

    return ''.join(errors)


def check_edge(in_fc, tolerance, out_chk):
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
    f.write('OID, ErrorID, X, Y, Bearing, Angle\n')

    # result = check_mini_edge(in_fc, tolerance, 1, 0)
    result = check_parallel(check_mini_edge, in_fc, tolerance)
    f.write(filter_errors(result))
    f.close()


def filter_errors(result):
    filter_result = []

    errors = result.split("\n")
    for i in xrange(0, len(errors) - 2):
        irecord = errors[i].split(", ")
        ipx, ipy = irecord[2], irecord[3]
        for j in xrange(i + 1, len(errors) - 1):
            jrecord = errors[j].split(", ")
            jpx, jpy = jrecord[2], jrecord[3]
            if ipx == jpx and ipy == jpy:
                filter_result.append(errors[i])
                break

    return "\n".join(filter_result)


if __name__ == "__main__":
    in_fc = arcpy.GetParameterAsText(0)
    tolerance1 = arcpy.GetParameterAsText(1)
    tolerance2 = arcpy.GetParameterAsText(2)
    out_chk = arcpy.GetParameterAsText(3)

    check_edge(in_fc, [float(tolerance1), float(tolerance2)], out_chk)
