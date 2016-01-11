# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

import os
import arcpy


def check_unique_id_task(in_fc, field):
    desc = arcpy.Describe(in_fc)
    errors = []

    _fields = ["OID@", "SHAPE@XY", field]
    cursor = arcpy.da.SearchCursor(in_fc, ["OID@", "SHAPE@XY", field],
                                   spatial_reference=desc.spatialReference.GCS,
                                   sql_clause = (None, 'order by ' + field))
    row1 = cursor.next()
    oid, value = row1[0], row1[2]
    for row in cursor:
        if row[2] == value:
            errors.append('{0}, {1}, {2}, {3}, {4}, {5}\n'
                          .format(row[0], 'ERR07', row[1][0], row[1][1], oid, value))
        else:
            oid, value = row[0], row[2]
    del cursor

    return ''.join(errors)


def check_unique_id(in_fc, field, out_chk):
    if not arcpy.Exists(in_fc):
        arcpy.AddIDMessage("ERROR", 110, in_fc)
        raise SystemExit()

    ext = os.path.splitext(out_chk)[1]
    if ext != '.csv':
        out_chk += '.csv'
    f = open(out_chk, 'w')
    f.write('OID, ErrorID, X, Y, OID2, Value\n')

    result = check_unique_id_task(in_fc, field)
    f.write(result)
    f.close()


if __name__ == "__main__":
    in_fc = arcpy.GetParameterAsText(0)
    field = arcpy.GetParameterAsText(1)
    out_chk = arcpy.GetParameterAsText(2)

    check_unique_id(in_fc, field, out_chk)