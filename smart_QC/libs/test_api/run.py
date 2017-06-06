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
from .report import TestReport, TestResult
from .variables import Scope, EvalExpression, ConstantStr
import ast
import requests
# import json
from django.conf import settings
import uuid
import os
# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)
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
        self.scope = Scope()  # 包括全局、本地和当前
        # output to a file
        self.output_name = str(uuid.uuid1()) + '.html'
        self.output_path = os.path.join(os.path.dirname(settings.STATIC_ROOT), 'test_report/').replace('\\', '/')
        self.title = 'My api test'
        self.description = 'This demonstrates the report output by Smart_QC.'
        fp = open(self.output_path + self.output_name, 'wb')
        self.report = TestReport(
            stream=fp,
            title=self.title,
            description=self.description
        )
        self.result = TestResult()

    def run(self):
        selected_case_reordered = self._reorder(self.selected_case, self.case_ids)
        for c in selected_case_reordered:
            self.result.start_case()
            if c.case_type == 0:  # Single API
                self._single_api_replay(c)
                # add replay log, update case status
                self.scope.clear_temp()  # 清理当前scope
            elif c.case_type == 1:  # APIGroup
                self._api_group_replay(c)
                # add replay log, update case status
                self.scope.clear_temp()  # 清理当前scope
            self.result.add_result()
            # 更新对应用例last_run_status
        self.report.generateReport(self.result)
        logger.info("Report generated:%s" % (self.output_path + self.output_name))
        # 更新report记录
        return None

    def stop(self):
        self.session.close()

    def email_report(self):
        pass

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
        logger.info('invoke _single_api_replay %s %s' % (INVOKE_LEVEL["current"], case.id))
        # run setup
        steps = case.step.all()
        for step in steps:
            self.result.current_case.start_step()
            if step.usage == 2:  # run "send_request" step
                # pre request
                request_parser = RequestParser(case, self.scope, self.valid_hosts)
                request_parser.parse_all()
                request_params = request_parser.final_params
                logger.info('request_params: %s' % request_params)
                # send request
                req = requests.Request(**request_params).prepare()
                res = self.session.send(req, verify=False)
                self.scope.update('current_ns', {'response': res})  # 将运行结果插入
                self.result.current_case.add_success(step.name, '22222')  #
            else:  # run other step
                step_runner = StepRunner(step, self.scope)
                step_runner.run()
                self.scope = step_runner.final_scope()
                self.result.current_case.add_success(step.name, '22222')  #
            self.result.current_case.stop_step()

            # run teardown
            # # pre request: prepare request params, running setup
            # send_host = case.host.name
            # for host_tuple in self.valid_hosts:
            #     if case.host.module == host_tuple[1]:
            #         send_host = host_tuple[0]
            #         break
            # send_url = case.protocol + '://' + send_host + case.path
            # send_headers = case.request_headers if case.request_headers else None
            # send_data = case.data if case.data else None
            # send_params = case.params if case.params else None
            # # print(send_url, type(send_url))
            # # print(send_data, type(send_data))
            # # print(send_params, type(send_params))
            #
            # # send request
            # req = requests.Request(method=case.method, url=send_url, headers=send_headers, data=send_data,
            #                        params=send_params).prepare()
            # res = self.session.send(req, verify=False)
            # from robot.libraries.BuiltIn import _Misc
            # a = _Misc()
            # ns = {"hh": 4}
            # # b=a.evaluate('random.randint(0, hh) ', modules='random, sys', namespace=ns)
            # c = a.evaluate('1 + hh', namespace=ns)
            # print(c)
            # # after request: asserting, running teardown, new or update variables
            # # d=res.content
            # # import json
            # # e=json.loads(d)
            # e = res.json()
            # print(e.get("resultInfo"))

            # print(res.request.url)

    def _api_group_replay(self, case):
        sub_cases = case.invoke_cases.all()
        for c in sub_cases:
            if c.case_type == 0:  # Single API
                self._single_api_replay(c)
            elif c.case_type == 1 and INVOKE_LEVEL["current"] <= INVOKE_LEVEL["to"]:  # APIGroup
                logger.info('invoke _api_group_replay %s %s' % (INVOKE_LEVEL["current"], c.id))
                INVOKE_LEVEL["current"] += 1
                self._api_group_replay(c)
            else:
                logger.info('invoke limited %s %s' % (INVOKE_LEVEL["current"], c.id))
                INVOKE_LEVEL["current"] = INVOKE_LEVEL["from"]
                continue


class StepRunner(object):
    def __init__(self, step, scope):
        self.step = step
        self.scope = scope
        self.variable = step.variable
        self.modules = step.modules
        self.namespace = ast.literal_eval(step.namespace)
        self.expression = step.expression
        self.result = {}

    def run(self):
        input_modules = self.modules if self.modules else []
        self.scope.current_ns.update(self.scope.global_ns)
        self.scope.current_ns.update(self.scope.local_ns)
        self.scope.current_ns.update((m, __import__(m)) for m in input_modules if m)
        self.scope.current_ns.update(self.namespace)
        evaled = EvalExpression(self.expression, self.scope)
        variable_value = evaled.evaluate()
        self.result[self.variable] = variable_value
        self.scope = evaled.scope
        logger.info("%s evaluate result is: %s %s" % (self.expression, type(variable_value), variable_value))

    def final_scope(self):
        if self.step.variable:
            if self.step.global_scope:
                self.scope.update('global_ns', self.result)  # 加入self.variable，self.variable_ns
            else:
                self.scope.update('current_ns', self.result)
        return self.scope


class RequestParser(object):
    scope = Scope()
    final_params = {}

    def __init__(self, case, scope, valid_hosts):
        self.scope = scope
        self.case = case
        self.valid_hosts = valid_hosts

    def parse_all(self):
        # 依次处理url,header等信息
        self.final_params['method'] = self.case.method
        send_host = self.case.host.name
        for host_tuple in self.valid_hosts:
            if self.case.host.module == host_tuple[1]:
                send_host = host_tuple[0]
                break
        url = self.case.protocol + '://' + send_host + self.case.path
        self.final_params['url'] = url
        final_params = {"headers": self.case.request_headers, "data": self.case.data, "params": self.case.params}
        for k, v in final_params.items():
            v = self._parse(v)
            self.final_params.update(((k, v),))

    def _parse(self, to_parse):
        if to_parse:
            if isinstance(to_parse, unicode):
                constant_str_obj = ConstantStr(input_str=to_parse, scope=self.scope)
                return constant_str_obj.evaluate()
            elif isinstance(to_parse, (dict, list)):
                constant_str_obj = ConstantStr(input_str=str(to_parse), scope=self.scope)
                return ast.literal_eval(constant_str_obj.evaluate())
            # elif isinstance(to_parse, list):
            #     constant_str_obj = ConstantStr(input_str=str(to_parse), scope=self.scope)
            #     return ast.literal_eval(constant_str_obj.evaluate())
            else:
                return to_parse
        else:
            return to_parse
