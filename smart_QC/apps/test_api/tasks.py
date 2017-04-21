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
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
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
    valid_hosts = TestHost.objects.filter(testenvironment__id=test_environment.get('id')).values_list('name',
                                                                                                      'module')
    case_ids = [i.get('id') for i in case]
    selected_case = Case.objects.filter(id__in=case_ids).order_by()
    # reorder query set
    selected_case_reordered = _reorder(selected_case, case_ids)
    for c in selected_case_reordered:
        if c.case_type == 0:  # Single API
            _single_api_replay(valid_hosts, c)
            # add replay log, update case status
        elif c.case_type == 1:  # APIGroup
            _api_group_replay(valid_hosts, c)
            # add replay log, update case status
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
    # 替换host, 运行参数化，运行setup, 发起request，断言，添加或修改参数，运行teardown
    INVOKE_LEVEL["current"] = INVOKE_LEVEL["from"]
    print('invoke _single_api_replay %s %s' % (INVOKE_LEVEL["current"], case.id))
    # pre request: prepare request params, run setup
    send_host = case.host.name
    for host_tuple in valid_hosts:
        if case.host.module == host_tuple[1]:
            send_host = host_tuple[0]
            break
    send_url = case.protocol + '://' + send_host + case.path
    send_headers = case.request_headers if case.request_headers else None
    send_data = case.data if case.data else None
    send_params = case.params if case.params else None
    # print(send_url, type(send_url))
    # print(send_data, type(send_data))
    # print(send_params, type(send_params))

    # send request
    s = requests.Session()
    req = requests.Request(method=case.method, url=send_url, headers=send_headers, data=send_data,
                           params=send_params).prepare()
    res = s.send(req, verify=False)
    from robot.running.builder import StepBuilder
    # step = StepBuilder()
    from robot.libraries.BuiltIn import _Misc
    a=_Misc()
    ns = {"${hh}":4}
    # b=a.evaluate('random.randint(0, hh) ', modules='random, sys', namespace=ns)
    c=a.evaluate('1 + ${hh}', namespace=ns)
    print(c)
    # from robot.
    # after request: asserting, run teardown, new or update variables
    print(res.request.url)
    print(res.content)


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
