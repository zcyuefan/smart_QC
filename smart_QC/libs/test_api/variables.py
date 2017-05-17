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
from asteval import Interpreter


class Scope(object):
    global_ns = {}
    current_ns = {}
    local_ns = {}

    def __init__(self, **kwargs):
        self.global_ns = kwargs.pop('global_ns', {})
        self.current_ns = kwargs.pop('current_ns', {})
        self.local_ns = kwargs.pop('local_ns', {})

    def update(self, scope_type, value):
        if scope_type == 'global_ns':
            self.global_ns.update(value)
        elif scope_type == 'current_ns':
            self.current_ns.update(value)
        elif scope_type == 'local_ns':
            self.local_ns.update(value)

    def clear_temp(self):
        self.current_ns = {}
        self.local_ns = {}

    def clear_all(self):
        self.clear_temp()
        self.global_ns = {}


class StrWithVariable(object):
    input_str = ""
    parsed_str = ""
    scope = Scope()

    def __init__(self, input_str, scope):
        self.input_str = input_str
        self.scope = scope

    def finder(self):
        pass

    def store(self):
        pass

    def parse(self):
        return self.parsed_str

    def _escape(self):
        #  忽略掉\${variable}
        pass

    def replace(self):
        pass

    def _lower_variable_name(self):
        pass


class EvalExpression(StrWithVariable):
    def evaluate(self):
        self.parse()
        aeval = Interpreter()
        aeval.symtable.update(self.scope.current_ns)
        result = aeval(self.parsed_str)
        self.scope.current_ns = aeval.symtable
        return result


class ConstantStr(StrWithVariable):
    def evaluate(self):
        pass


class Variable(object):
    def __init__(self, name):
        self.name = name
        self.value = None


    def find(self):
        # 在local和global中寻找变量
        pass

    def eval(self):
        pass

    def update_namespace(self):
        pass
