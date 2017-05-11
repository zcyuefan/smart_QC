#!/usr/bin/env python
# encoding=utf-8

# Author zhangchao@jinwantai.com
# date:2017/5/11
# topic: 
# update: 

"""
file doc
"""
from __future__ import unicode_literals


class VariableString(object):
    def find_variables(self):
        pass

    def _escape(self):
        #  忽略掉\${variable}
        pass

    def replace(self):
        pass

    def _lower_variable_name(self):
        pass


class Variable(object):
    def __init__(self, global_namespace):
        self.global_ns = global_namespace
        self.local_ns = {}

    def find(self):
        # 在local和global中寻找变量
        pass

    def eval(self):
        pass

    def update_namespace(self):
        pass
