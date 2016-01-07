# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

import arcpy
from area import get_rings
from bearing import bearing, angle



def bearing_test():
    print "hello"
    in_fc = 'C:\\Users\\Sam\\Documents\\ArcGIS\\Default.gdb\\Export_Output_2'
    desc = arcpy.Describe(in_fc)
    cursor = arcpy.da.SearchCursor(in_fc, ["OID@", "SHAPE@"], spatial_reference=desc.spatialReference.GCS)
    for row in cursor:
        rings = get_rings(row[1])
        for ring in rings:
            for i in xrange(0, len(ring) - 1):
                p1, p2, p3 = i, i + 1, i + 2
                if p3 == len(ring):
                    p3 = 1

                _bearing = bearing(ring[p1], ring[p2])
                _angle = angle(ring[p1], ring[p2], ring[p3])

                print (_bearing, _angle)

