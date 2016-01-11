# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

import os
import re
import arcpy
from parallel import check_parallel

def check_rare_name_task(args, cpus, pid):
    in_fc = args[0]
    fields = args[1]
    error_id = "ERR04"
    layer = os.path.basename(in_fc)
    content = "道路名称字段不能含有不合理的字符"
    description = "图层【{0}】的ID为【{1}】的要素，道路名称字段不能含有不合理的字符。"
    warning = "不忽略"

    desc = arcpy.Describe(in_fc)
    errors = []
    pattern = re.compile(u"[ ~!！.·#￥%…&*]")

    _fields = ["OID@", "SHAPE@XY"] + fields
    cursor = arcpy.da.SearchCursor(in_fc, _fields, spatial_reference=desc.spatialReference.GCS)
    for row in cursor:
        if row[0] % cpus != pid:
            continue

        for i in xrange(2, len(row)):
            if not row[i]:
                continue

            # row[i] is a unicode string
            display_name = row[i].encode("utf-8")
            field = _fields[i]
            match = pattern.search(row[i])
            if match:
                errors.append('{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}\n'
                              .format(row[0], error_id, layer, content, description.format(layer, row[0]), row[1][0], row[1][1], warning))
                continue

            try:
                row[i].encode("gb2312")
            except UnicodeEncodeError:
                errors.append('{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}\n'
                              .format(row[0], error_id, layer, content, description.format(layer, row[0]), row[1][0], row[1][1], warning))
                continue
    del cursor

    return ''.join(errors)


def check_rare_name(in_fc, fields, out_chk):
    if not arcpy.Exists(in_fc):
        arcpy.AddIDMessage("ERROR", 110, in_fc)
        raise SystemExit()

    ext = os.path.splitext(out_chk)[1]
    if ext != '.csv':
        out_chk += '.csv'
    f = open(out_chk, 'w')
    f.write('OID, ErrorID, Layer, InspectionContent, Description, X, Y, Warning\n')

    # result = check_rare_name_task((in_fc, fields), 1, 0)
    result = check_parallel(check_rare_name_task, (in_fc, fields))
    f.write(result)
    f.close()


if __name__ == "__main__":
    in_fc = arcpy.GetParameterAsText(0)
    fields = arcpy.GetParameterAsText(1)
    out_chk = arcpy.GetParameterAsText(2)

    check_rare_name(in_fc, fields.split(";"), out_chk)
