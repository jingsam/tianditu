# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

import os
import multiprocessing
import json
import arcpy
from area import ring_area


def check_mini_area(in_fc, tolerance, cpus, pid):
    desc = arcpy.Describe(in_fc)
    errors = []

    cursor = arcpy.da.SearchCursor(in_fc, ["OID@", "SHAPE@"], spatial_reference=desc.spatialReference.GCS)
    for row in cursor:
        if row[0] % cpus != pid:
            continue

        polygon = json.loads(row[1].JSON)
        if not polygon.get("rings"):
            continue

        for ring in polygon.get("rings"):
            area = ring_area(ring)
            if abs(area) <= tolerance:
                errors.append('{0}, {1}, {2}, {3}, {4}\n'.format(row[0], 'ERR05', ring[0][0], ring[0][1], abs(area)))
    del cursor

    return ''.join(errors)


def check_hole(n_fc, tolerance, out_chk):
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
    f.write('OID, ErrorID, X, Y, Area\n')

    result = check_mini_area(in_fc, tolerance, 1, 0)
    f.write(result)
    f.close()


def check_hole_parallel(in_fc, tolerance, out_chk):
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
    f.write('OID, ErrorID, X, Y, Area\n')

    multiprocessing.freeze_support()
    pool = multiprocessing.Pool()
    cpus = multiprocessing.cpu_count()
    results = []

    for pid in xrange(0, cpus):
        result = pool.apply_async(check_mini_area, args=(in_fc, tolerance, cpus, pid))
        results.append(result)

    pool.close()
    pool.join()

    for result in results:
        f.write(result.get())
    f.close()


if __name__ == "__main__":
    in_fc = arcpy.GetParameterAsText(0)
    tolerance = arcpy.GetParameterAsText(1)
    out_chk = arcpy.GetParameterAsText(2)

    check_hole_parallel(in_fc, float(tolerance), out_chk)
