# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

import os
import arcpy
from area import get_rings
from bearing import bearing, angle
from parallel import check_parallel


def check_edge_task(args, cpus, pid):
    in_fc = args[0]
    tolerance1 = args[1]
    tolerance2 = args[2]
    error_id = "ERR03"
    layer = os.path.basename(in_fc)
    content = "接边线角度检查"
    description = "图层【{0}】的ID为【{1}】的要素，接边线角度不合理。"
    warning = "不忽略"

    desc = arcpy.Describe(in_fc)
    errors = []

    cursor = arcpy.da.SearchCursor(in_fc, ["OID@", "SHAPE@"], spatial_reference=desc.spatialReference.GCS)
    for row in cursor:
        if row[0] % cpus != pid:
            continue

        rings = get_rings(row[1])
        for ring in rings:
            for i in xrange(0, len(ring) - 1):
                p1, p2, p3, p4 = i, i + 1, i + 2, i + 3
                if p3 == len(ring) - 1:
                    p4 = 1
                elif p3 == len(ring):
                    p3, p4 = 1, 2

                _bearing = bearing(ring[p2], ring[p3])
                _angle1 = angle(ring[p1], ring[p2], ring[p3])
                _angle2 = angle(ring[p2], ring[p3], ring[p4])
                _angle = _angle1 + _angle2

                min_bearing = min(abs(_bearing), abs(_bearing - 90), abs(_bearing + 90), abs(_bearing - 180), abs(_bearing + 180))
                min_angle1 = min(abs(90 - _angle), abs(180 - _angle), abs(270 - _angle))
                min_angle2 = min(abs(90 - _angle1), abs(90 - _angle2))

                p = p2 if _bearing >= 0 else p3
                if min_bearing <= tolerance1 and min_angle1 <= tolerance2 and min_angle2 > tolerance2:
                    errors.append('{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}\n'
                                  .format(row[0], error_id, layer, content, description.format(layer, row[0]), ring[0].X, ring[0].Y, warning))
    del cursor

    return ''.join(errors)


def check_edge(in_fc, tolerance1, tolerance2, out_chk):
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
    f.write('OID, ErrorID, Layer, InspectionContent, Description, X, Y, Warning\n')

    # result = check_edge_task((in_fc, tolerance1, tolerance2), 1, 0)
    result = check_parallel(check_edge_task, (in_fc, tolerance1, tolerance2))
    f.write(filter_errors(result, tolerance2))
    f.close()


def filter_errors(result, tolerance2):
    filter_result = []

    errors = result.split("\n")
    for i in xrange(0, len(errors) - 2):
        irecord = errors[i].split(", ")
        ipx, ipy, iangle = float(irecord[2]), float(irecord[3]), float(irecord[5])
        for j in xrange(i + 1, len(errors) - 1):
            jrecord = errors[j].split(", ")
            jpx, jpy, jangle = float(jrecord[2]), float(jrecord[3]), float(jrecord[5])
            min_angle = min(abs(360 - (iangle + jangle)), abs(180 - (iangle + jangle)))
            if ipx == jpx and ipy == jpy and min_angle <= tolerance2:
                filter_result.append(errors[i])
                break

    return "\n".join(filter_result)


if __name__ == "__main__":
    in_fc = arcpy.GetParameterAsText(0)
    tolerance1 = arcpy.GetParameterAsText(1)
    tolerance2 = arcpy.GetParameterAsText(2)
    out_chk = arcpy.GetParameterAsText(3)

    check_edge(in_fc, float(tolerance1), float(tolerance2), out_chk)
