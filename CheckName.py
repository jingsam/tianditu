# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

import os
import re
import arcpy
from parallel import check_parallel

def check_err_name(args, cpus, pid):
    in_fc = args[0]
    fields = args[1]

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
                errors.append('{0}, {1}, {2}, {3}, {4}, {5}\n'.format(row[0], 'ERR07', row[1][0], row[1][1], field, display_name))
                continue

            try:
                row[i].encode("gb2312")
            except UnicodeEncodeError:
                errors.append('{0}, {1}, {2}, {3}, {4}, {5}\n'.format(row[0], 'ERR07', row[1][0], row[1][1], field, display_name))
                continue
    del cursor

    return ''.join(errors)


def check_name(in_fc, fields, out_chk):
    if not arcpy.Exists(in_fc):
        arcpy.AddIDMessage("ERROR", 110, in_fc)
        raise SystemExit()

    ext = os.path.splitext(out_chk)[1]
    if ext != '.csv':
        out_chk += '.csv'
    f = open(out_chk, 'w')
    f.write('OID, ErrorID, X, Y, Field, Name\n')

    # result = check_err_name((in_fc, fields), 1, 0)
    result = check_parallel(check_err_name, (in_fc, fields))
    f.write(result)
    f.close()


if __name__ == "__main__":
    in_fc = arcpy.GetParameterAsText(0)
    fields = arcpy.GetParameterAsText(1)
    out_chk = arcpy.GetParameterAsText(2)

    check_name(in_fc, fields.split(";"), out_chk)
