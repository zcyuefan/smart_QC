#!/usr/bin/env python
# encoding=utf-8

# Author zhangchao@jinwantai.com
# date:2017/5/9
# topic: 
# update: 

"""
 调度并运行cases
"""
from __future__ import unicode_literals
from smart_QC.apps.test_api.models import TestHost, Case
# from parse import AllCaseParse, CaseParse
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
# 限制api group调用其他用例的层数，避免相互调用产生死循环，分别是[初值, 当前递归层数, 限制递归层数]
# INVOKE_LEVEL = [1, 1, 3]
INVOKE_LEVEL = {"from": 1, "current": 1, "to": 3}


class Runner(object):
    def __init__(self, test_environment, case):
        self.valid_hosts = TestHost.objects.filter(testenvironment__id=test_environment.get('id')).values_list('name',
                                                                                                          'module')
        self.case_ids = [i.get('id') for i in case]
        self.selected_case = Case.objects.filter(id__in=self.case_ids)
        self.session = requests.Session()
        self.namespace = {}  # 包括全局、本地和当前
        self.report = {}  # 测试报告对象，后面会添加model并render
        # self.global_ns = {}
        # self.local_ns = {}
        # self.current_ns = {}

    def run(self):
        selected_case_reordered = self._reorder(self.selected_case, self.case_ids)
        for c in selected_case_reordered:
            if c.case_type == 0:  # Single API
                self._single_api_replay(c)
                # add replay log, update case status
            elif c.case_type == 1:  # APIGroup
                self._api_group_replay(c)
                # add replay log, update case status
        return None

    def stop(self):
        self.session.close()

    def _reorder(self, query_set, id_list):
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

    def _single_api_replay(self, case):
        # 替换host, 运行参数化，运行setup, 发起request，断言，添加或修改参数，运行teardown
        INVOKE_LEVEL["current"] = INVOKE_LEVEL["from"]
        print('invoke _single_api_replay %s %s' % (INVOKE_LEVEL["current"], case.id))
        # 定义命名空间
        self.namespace.local.update  # 获取当前用例命名空间
        self.current_ns = {}
        # pre request: prepare request params, running setup
        send_host = case.host.name
        for host_tuple in self.valid_hosts:
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
        req = requests.Request(method=case.method, url=send_url, headers=send_headers, data=send_data,
                               params=send_params).prepare()
        res = self.session.send(req, verify=False)
        from robot.libraries.BuiltIn import _Misc
        a = _Misc()
        ns = {"hh": 4}
        # b=a.evaluate('random.randint(0, hh) ', modules='random, sys', namespace=ns)
        c = a.evaluate('1 + hh', namespace=ns)
        print(c)
        # after request: asserting, running teardown, new or update variables
        # d=res.content
        # import json
        # e=json.loads(d)
        e = res.json()
        print(e.get("resultInfo"))

        print(res.request.url)
        print(res.content)
        print(res.status_code)

    def _api_group_replay(self, case):
        sub_cases = case.invoke_cases.all()
        for c in sub_cases:
            if c.case_type == 0:  # Single API
                self._single_api_replay(c)
            elif c.case_type == 1 and INVOKE_LEVEL["current"] <= INVOKE_LEVEL["to"]:  # APIGroup
                print('invoke _api_group_replay %s %s' % (INVOKE_LEVEL["current"], c.id))
                INVOKE_LEVEL["current"] += 1
                self._api_group_replay(c)
            else:
                print('invoke limited %s %s' % (INVOKE_LEVEL["current"], c.id))
                INVOKE_LEVEL["current"] = INVOKE_LEVEL["from"]
                continue