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
import re


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
        self.current_ns.clear()
        self.local_ns.clear()

    def clear_all(self):
        self.clear_temp()
        self.global_ns.clear()


class StrWithVariable(object):
    input_str = ""
    parsed_str = ""
    scope = Scope()
    variable_list = []
    variable_dict = {}

    def __init__(self, input_str, scope):
        self.input_str = input_str
        self.parsed_str = input_str
        self.scope = scope

    def find(self):
        if isinstance(self.input_str, unicode) and '$' in self.input_str:
            variable_pattern = re.compile(r'\$\{.*?\}', re.M)
            self.variable_list = variable_pattern.findall(self.input_str)
        return self.variable_list

    def get_value(self):
        aeval = Interpreter()
        aeval.symtable.update(self.scope.current_ns)
        for var in self.variable_list:
            self.variable_dict.update((var, aeval(var[2:-1].strip(' '))))
        return self.variable_dict

    def parse(self):
        for var in self.variable_list:
            var_name = var[2:-1].strip(' ')
            self.parsed_str.replace(var, var_name)
        return self.parsed_str


class EvalExpression(StrWithVariable):
    def evaluate(self):
        self.find()
        self.parse()
        aeval = Interpreter()
        aeval.symtable.update(self.scope.current_ns)
        result = aeval(self.parsed_str)
        self.scope.current_ns = aeval.symtable
        return result


class ConstantStr(StrWithVariable):
    def evaluate(self):
        self.find()
        aeval = Interpreter()
        aeval.symtable.update(self.scope.current_ns)
        for var in self.variable_list:
            if var:
                self.parsed_str = self.parsed_str.replace(var, str(aeval(var[2:-1].strip(' '))))
        return self.parsed_str
