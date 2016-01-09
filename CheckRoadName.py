# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

import os
import arcpy
from parallel import check_parallel


def check_road_name_task(args, cpus, pid):
    in_fc = args[0]
    fields = args[1]

    desc = arcpy.Describe(in_fc)
    errors = []

    _fields = ["OID@", "SHAPE@XY"] + fields
    cursor = arcpy.da.SearchCursor(in_fc, _fields, spatial_reference=desc.spatialReference.GCS)
    for row in cursor:
        if row[0] % cpus != pid:
            continue

        all_names = [row[i] for i in xrange(2, len(row))]
        names = [name for name in all_names if name.strip()]
        if len(names) == 0:
            continue

        if len(set(names)) < len(names):
            errors.append('{0}, {1}, {2}, {3}, {4}\n'
                          .format(row[0], 'ERR04', row[1][0], row[1][1], u';'.join(all_names).encode("utf-8")))
            continue

        for name in names:
            if all_names.index(name) >= len(names):
                errors.append('{0}, {1}, {2}, {3}, {4}\n'
                          .format(row[0], 'ERR04', row[1][0], row[1][1], u';'.join(all_names).encode("utf-8")))
                break
    del cursor

    return ''.join(errors)


def check_road_name(in_fc, fields, out_chk):
    if not arcpy.Exists(in_fc):
        arcpy.AddIDMessage("ERROR", 110, in_fc)
        raise SystemExit()

    ext = os.path.splitext(out_chk)[1]
    if ext != '.csv':
        out_chk += '.csv'
    f = open(out_chk, 'w')
    f.write('OID, ErrorID, X, Y, Field, Names\n')

    # result = check_road_name_task((in_fc, fields), 1, 0)
    result = check_parallel(check_road_name_task, (in_fc, fields))
    f.write(result)
    f.close()


if __name__ == "__main__":
    in_fc = arcpy.GetParameterAsText(0)
    fields = arcpy.GetParameterAsText(1)
    out_chk = arcpy.GetParameterAsText(2)

    check_road_name(in_fc, fields.split(';'), out_chk)