# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

import os
import re
import arcpy
from parallel import check_parallel

def check_err_name(in_fc, fields, cpus, pid):
    desc = arcpy.Describe(in_fc)
    errors = []
    # pattern = re.compile(r'[~!@#$%^&*]')

    _fields = ["OID@", "SHAPE@XY"] + fields
    cursor = arcpy.da.SearchCursor(in_fc, _fields, spatial_reference=desc.spatialReference.GCS)
    for row in cursor:
        if row[0] % cpus != pid:
            continue

        for i in xrange(2, len(row)):
            # match = pattern.search(row[i])
            name = row[i].encode('utf-8')
            if name:
                print name
                errors.append('{0}, {1}, {2}, {3}, {4}, {5}\n'.format(row[0], 'ERR07', row[1][0], row[1][1], _fields[i], 0))

    del cursor


def check_road_name(in_fc, fields, out_chk):
    if not arcpy.Exists(in_fc):
        arcpy.AddIDMessage("ERROR", 110, in_fc)
        raise SystemExit()

    ext = os.path.splitext(out_chk)[1]
    if ext != '.csv':
        out_chk += '.csv'
    f = open(out_chk, 'w')
    f.write('OID, ErrorID, X, Y, Field, Name\n')

    # result = check_err_name(in_fc, fields, 1, 0)
    result = check_parallel(check_err_name, in_fc, fields)
    f.write(result)
    f.close()


if __name__ == "__main__":
    in_fc = arcpy.GetParameterAsText(0)
    fields = arcpy.GetParameterAsText(1)
    out_chk = arcpy.GetParameterAsText(2)

    check_road_name(in_fc, fields.split(";"), out_chk)
