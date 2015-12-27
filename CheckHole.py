# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

import os
import arcpy


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
    f.write('OID, ErrorID, X, Y, area\n')

    cursor = arcpy.da.SearchCursor(in_fc, ["SHAPE@", "OID@"], spatial_reference=desc.spatialReference.GCS)
    for row in cursor:
        for part in row[0]:
            area = arcpy.Polygon(part, desc.spatialReference.GCS).getArea('geodesic')
            if abs(area) <= tolerance:
                f.write('{0}, {1}, {2}, {3}, {4}\n'.format(row[1], 'ERR05', part[0].X, part[0].Y, area))
                break
    del cursor
    f.close()


if __name__ == "__main__":
    in_fc = arcpy.GetParameterAsText(0)
    tolerance = arcpy.GetParameterAsText(1)
    out_chk = arcpy.GetParameterAsText(2)

    check_hole(in_fc, float(tolerance), out_chk)

