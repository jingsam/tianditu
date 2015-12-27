# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

import arcpy


def CheckService(in_fc, field):
    if not arcpy.Exists(in_fc):
        arcpy.AddIDMessage("ERROR", 110, in_fc)
        raise SystemExit()

    desc = arcpy.Describe(in_fc)
    if desc.shapeType.lower() not in ("polygon", "polyline"):
        arcpy.AddIDMessage("ERROR", 931)
        raise SystemExit()

    if field not in desc.fields:
        arcpy.AddField_management(in_fc, field, "DOUBLE")

    arcpy.CalculateField_management(in_fc, field, "!shape.length@kilometers!", "PYTHON_9.3")

if __name__ == "__main__":
    input_fc = arcpy.GetParameterAsText(0)
    field = arcpy.GetParameterAsText(1)
