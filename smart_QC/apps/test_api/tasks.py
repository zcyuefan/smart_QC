#!/usr/bin/env python
# encoding=utf-8

# Author zhangchao@jinwantai.com
# date:2017/3/29
# topic: 
# update: 

"""
celery异步任务
"""
from __future__ import unicode_literals
from celery import shared_task
from models import TestHost, Case

# 限制api group调用其他用例的层数，避免相互调用产生死循环，分别是[初值, 当前递归层数, 限制递归层数]
# INVOKE_LEVEL = [1, 1, 3]
INVOKE_LEVEL = {"from": 1, "current": 1, "to": 3}

@shared_task
def run_case(test_environment, case):
    """
    执行接口测试用例
    :param test_environment:测试环境
    :param case:测试用例
    :return:
    """
    valid_hosts = TestHost.objects.filter(testenvironment__id=test_environment.get('id')).values_list('id', 'name',
                                                                                                      'module')
    case_ids = [i.get('id') for i in case]
    selected_case = Case.objects.filter(id__in=case_ids).order_by()
    # reorder query set
    selected_case_reordered = _reorder(selected_case, case_ids)
    for c in selected_case_reordered:
        if c.case_type == 0:  # Single API
            _single_api_replay(valid_hosts, c)
        elif c.case_type == 1:  # APIGroup
            _api_group_replay(valid_hosts, c)
    return None


def _reorder(query_set, id_list):
    new_set = []
    try:
        for i in id_list:
            for q in query_set:
                if q.id == int(i):
                    new_set.append(q)
    except Exception:
        pass
    finally:
        return new_set


def _single_api_replay(valid_hosts, case):
    # 替换host, 运行参数化，运行setup, 发起request，断言，添加或修改参数，运行teardown，新增replaylog
    INVOKE_LEVEL["current"] = INVOKE_LEVEL["from"]
    print(INVOKE_LEVEL)
    print('invoke _single_api_replay %s %s' % (INVOKE_LEVEL["current"], case.id))


def _api_group_replay(valid_hosts, case):
    sub_case_ids = case.invoke_cases.values_list('id')
    sub_cases = Case.objects.filter(id__in=sub_case_ids)
    id_list = [i[0] for i in sub_case_ids]
    sub_cases_reorder = _reorder(sub_cases, id_list)
    for c in sub_cases_reorder:
        if c.case_type == 0:  # Single API
            _single_api_replay(valid_hosts, c)
        elif c.case_type == 1 and INVOKE_LEVEL["current"] <= INVOKE_LEVEL["to"]:  # APIGroup
            print('invoke _api_group_replay %s %s' % (INVOKE_LEVEL["current"], c.id))
            INVOKE_LEVEL["current"] += 1
            _api_group_replay(valid_hosts, c)
        else:
            print('invoke limited %s %s' % (INVOKE_LEVEL["current"], c.id))
            INVOKE_LEVEL["current"] = INVOKE_LEVEL["from"]
            continue


@shared_task
def add(x, y):
    return x + y
