# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

import re

test_str = u"你懐a"
test_str2 = "你懐a"
print repr(test_str)
print repr(test_str2.decode("utf-8"))
print repr(unicode(test_str2))

pattern = re.compile(u"[ ~!！.·#￥%…&*]")
match = pattern.search(test_str)
if match:
    print match.group()

try:
    test_str.encode("gb2312")
except UnicodeEncodeError:
    print test_str


