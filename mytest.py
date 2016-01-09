# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

import re

def get_pattern(keywords, rule):
    match = False if u'不' in rule else True
    pattern = u'|'.join(keywords)
    if u'包含关键字' in rule:
        return re.compile(pattern), match
    elif u'以关键字开头' in rule:
        return  re.compile(u'^(' + pattern + u')'), match
    elif u'以关键字结尾' in rule:
        return  re.compile(u'(' + pattern + u')$'), match

test_str = u"出口长江大桥"
pattern = get_pattern([u"桥",u"出口"], u"以关键字开头")
match = pattern[0].search(test_str)
print match.group()


