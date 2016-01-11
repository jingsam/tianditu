# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

import os
import arcpy


def check_unique_id_task(in_fc, field):
    desc = arcpy.Describe(in_fc)
    errors = []
    error_id = "ERR07"
    layer = os.path.basename(in_fc)
    content = "字段唯一值检查"
    description = "图层【{0}】的ID为【{1}，{2}】的要素，字段值【{3}】重复。"
    warning = "不忽略"

    _fields = ["OID@", "SHAPE@XY", field]
    cursor = arcpy.da.SearchCursor(in_fc, ["OID@", "SHAPE@XY", field],
                                   spatial_reference=desc.spatialReference.GCS,
                                   sql_clause = (None, 'order by ' + field))
    row1 = cursor.next()
    oid, value = row1[0], row1[2]
    for row in cursor:
        if row[2] == value:
            errors.append('{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}\n'
                          .format(row[0], error_id, layer, content, description.format(layer, oid, row[0], value), row[1][0], row[1][1], warning))
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
    f.write('OID, ErrorID, Layer, InspectionContent, Description, X, Y, Warning\n')

    result = check_unique_id_task(in_fc, field)
    f.write(result)
    f.close()


if __name__ == "__main__":
    in_fc = arcpy.GetParameterAsText(0)
    field = arcpy.GetParameterAsText(1)
    out_chk = arcpy.GetParameterAsText(2)

    check_unique_id(in_fc, field, out_chk)