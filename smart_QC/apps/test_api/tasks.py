#!/usr/bin/env python
# encoding=utf-8

# Author zhangchao@jinwantai.com
# date:2017/3/29
# topic: 
# update: 

"""
file doc
"""

from celery import shared_task

# @task()
# def do_request(obj):
#

@shared_task
def add(x, y):
    # import time
    # time.sleep(30)
    return x + y