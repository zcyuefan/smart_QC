#!/usr/bin/env python
# encoding=utf-8

# Author zhangchao@jinwantai.com
# date:2017/5/9
# topic: 
# update: 

"""
处理pre/after request中所有步骤的参数化实现，包括setup,teardown,variable更新，assert
"""
from __future__ import unicode_literals


class CaseParse(object):
    pass


class AllCaseParse(object):
    pass


class Base(object):
    pass


class Setup(Base):
    pass


class TearDown(Base):
    pass


class Assertion(Base):
    pass


class Variable(Base):
    pass


class Input(Base):
    pass
