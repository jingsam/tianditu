# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

import os
import re
import arcpy
from parallel import check_parallel


def get_pattern(keywords, rule):
    match = False if u'不' in rule else True
    pattern = u'|'.join(keywords)
    if u'包含关键字' in rule:
        return re.compile(pattern), match
    elif u'以关键字开头' in rule:
        return  re.compile(u'^(' + pattern + u')'), match
    elif u'以关键字结尾' in rule:
        return  re.compile(u'(' + pattern + u')$'), match


def check_name_task(args, cpus, pid):
    in_fc = args[0]
    fields = args[1]
    keywords = args[2]
    rule = args[3]
    error_id = "ERR05"
    layer = os.path.basename(in_fc)
    content = "属性值规则符合检查"
    description = "【{0}】图层中【{1}】字段值为【{2}】，不符合名称合法项规则。"
    warning = "不忽略"

    desc = arcpy.Describe(in_fc)
    errors = []
    pattern = get_pattern(keywords, rule)

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
            match = pattern[0].search(row[i])
            error = (pattern[1] and not match) or (not pattern[1] and match)
            if error:
                errors.append('{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}\n'
                              .format(row[0], error_id, layer, content, description.format(layer, field, display_name), row[1][0], row[1][1], warning))
                continue
    del cursor

    return ''.join(errors)


def check_name(in_fc, fields, keywords, rule, out_chk):
    if not arcpy.Exists(in_fc):
        arcpy.AddIDMessage("ERROR", 110, in_fc)
        raise SystemExit()

    ext = os.path.splitext(out_chk)[1]
    if ext != '.csv':
        out_chk += '.csv'
    f = open(out_chk, 'w')
    f.write('OID, ErrorID, Layer, InspectionContent, Description, X, Y, Warning\n')

    # result = check_name_task((in_fc, fields, keywords, rule), 1, 0)
    result = check_parallel(check_name_task, (in_fc, fields, keywords, rule))
    f.write(result)
    f.close()


if __name__ == "__main__":
    in_fc = arcpy.GetParameterAsText(0)
    fields = arcpy.GetParameterAsText(1)
    keywords = arcpy.GetParameterAsText(2)
    rule = arcpy.GetParameterAsText(3)
    out_chk = arcpy.GetParameterAsText(4)

    check_name(in_fc, fields.split(";"), keywords.split(";"), rule, out_chk)