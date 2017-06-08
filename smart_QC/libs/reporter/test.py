#!/usr/bin/env python
# encoding=utf-8

# Author zhangchao@jinwantai.com
# date:2017/5/31
# topic: 
# update: 

"""
file doc
"""
from __future__ import unicode_literals
import unittest
import BSTestRunner
from assertpy import assert_that

class MyTest(unittest.TestCase):
    def setUp(self):
        pass
    def test_sum(self):
        assert 1+1==2
    def test_minus(self):
        a=1
        b = a + 'd'
        assert 2 - 1 == 1
        self.assertEqual(1,1)

    def test_oo(self):
        assert 2 - 0 == 1, 'tytyyutyuytyuyty'

    def tearDown(self):
        pass


if __name__ == '__main__':
    BSTestRunner.main()