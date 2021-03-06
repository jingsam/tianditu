# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

import os
import arcpy
from area import get_rings, ring_area
from parallel import check_parallel


def check_hole_task(args, cpus, pid):
    in_fc = args[0]
    tolerance = args[1]
    error_id = "ERR01"
    layer = os.path.basename(in_fc)
    content = "多边形缝隙检查"
    description = "图层【{0}】的ID为【{1}】的要素，存在不合理的线缝隙、点缝隙。"
    warning = "不忽略"



    desc = arcpy.Describe(in_fc)
    errors = []

    cursor = arcpy.da.SearchCursor(in_fc, ["OID@", "SHAPE@"], spatial_reference=desc.spatialReference.GCS)
    for row in cursor:
        if row[0] % cpus != pid:
            continue

        rings = get_rings(row[1])
        for ring in rings:
            area = ring_area(ring)
            if abs(area) <= tolerance:
                errors.append('{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}\n'
                              .format(row[0], error_id, layer, content, description.format(layer, row[0]), ring[0].X, ring[0].Y, warning))
    del cursor

    return ''.join(errors)


def check_hole(in_fc, tolerance, out_chk):
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

    # result = check_hole_task((in_fc, tolerance), 1, 0)
    result = check_parallel(check_hole_task, (in_fc, tolerance))
    f.write(result)
    f.close()

if __name__ == "__main__":
    in_fc = arcpy.GetParameterAsText(0)
    tolerance = arcpy.GetParameterAsText(1)
    out_chk = arcpy.GetParameterAsText(2)

    check_hole(in_fc, float(tolerance), out_chk)
