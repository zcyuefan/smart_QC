#!/usr/bin/env python
# encoding=utf-8

# Author zhangchao@jinwantai.com
# date:2017/5/8
# topic: 
# update: 

"""
file doc
"""
from __future__ import unicode_literals
# from models import Script
import re


class Variable(object):
    def __init__(self, expression=""):
        self._expression = expression
        self._variables = {}

    def handle_variables(self):
        variable_list = self._get_variables()
        for variable in variable_list:
            self._handle_variable(variable)
        return self._expression, self._variables

    def _get_variables(self):
        # TODO 过滤掉注释内容
        if isinstance(self._expression, unicode) and '$' in self._expression:
            variable_pattern = re.compile(r'\$\{.*?\}', re.M)
            variable_list = variable_pattern.findall(self._expression)
        else:
            variable_list = []
        return variable_list

    def _handle_variable(self, variable):
        # TODO 每个
        # selected_case = Script.objects.filter(return_variable__in=)
        pass

if __name__ == "__main__":
    # a = Variable(expression="#${a} is ${b} + ${c.values} + 222")
    a = Variable(expression="""${a} is ${b} + ${c.values} + 222
    ${ddd}""")
    # a = Variable(expression="$qqq{a")
    b=a._get_variables()
    for c in b:
        print(c)
    # print(a._get_variables())
    # from robot.variables import VariableScopes
    # _variables = VariableScopes(None)
    # print(_variables)