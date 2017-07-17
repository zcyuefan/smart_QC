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
from smart_QC.apps.test_api.models import TestHost, Case, Report
from .report import TestReport, TestResult
from .variables import Scope, EvalExpression, ConstantStr
import ast
import requests
import traceback, sys, uuid, os, logging
from django.conf import settings
from assertpy import assert_that

# Get an instance of a logger
logger = logging.getLogger(__name__)
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
# 限制api group调用其他用例的层数，避免相互调用产生死循环，分别是[初值, 当前递归层数, 限制递归层数]
# INVOKE_LEVEL = [1, 1, 3]
INVOKE_LEVEL = {"from": 1, "current": 1, "to": 3}


class Runner(object):
    def __init__(self, test_environment, case, title, description):
        self.valid_hosts = TestHost.objects.filter(testenvironment__id=test_environment.get('id')).values_list('name',
                                                                                                               'module')
        self.case_ids = [i.get('id') for i in case]
        self.selected_case = Case.objects.filter(id__in=self.case_ids)
        self.session = requests.Session()
        self.scope = Scope()  # 包括全局、本地和当前
        # output to a file
        self.output_name = str(uuid.uuid1()) + '.html'
        self.output_path = settings.MEDIA_ROOT + '/test_report/'
        self.title = title
        self.description = description
        self.test_environment = test_environment.get('name', '')
        fp = open(self.output_path + self.output_name, 'wb')
        self.report = TestReport(
            stream=fp,
            title=title,
            description=description
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
            self.result.add_result(c.name, c.description)
            c.last_run_status = self.result.current_case.status  # 更新对应用例last_run_status
            c.save()  # 保存
        self.report.generateReport(self.result)
        logger.info("Report generated:%s" % (self.output_path + self.output_name))
        # 更新report记录
        Report.objects.create(title=self.title, description=self.description,
                              test_environment=self.test_environment, start_time=self.report.startTime,
                              duration=self.report.stopTime - self.report.startTime,
                              total=self.result.total_count,
                              pass_count=self.result.success_count, fail_count=self.result.failure_count,
                              error_count=self.result.error_count,
                              path=settings.MEDIA_URL + 'test_report/' + self.output_name, )
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
                try:
                    # pre request
                    request_parser = RequestParser(case, self.scope, self.valid_hosts)
                    request_parser.parse_all()
                    request_params = request_parser.final_params
                    logger.info('request_params: %s' % request_params)
                    # send request
                    req = requests.Request(**request_params).prepare()
                    res = self.session.send(req, verify=False)
                    self.scope.update('current_ns', {'response': res})  # 将运行结果插入
                    basic_output = """
    Request:
    %(method)s %(url)s
    %(request_headers)s

    %(data)s
    Response:
    %(status)s
    %(response_headers)s
    %(content)s
                    """ % dict(
                        method=res.request.method,
                        url=res.url,
                        status=str(res.status_code)+' '+res.reason,
                        request_headers='\r\n'.join([k+':'+str(v) for k, v in res.request.headers.items()]),
                        data=res.request.body,
                        response_headers='\r\n'.join([k+':'+str(v) for k, v in res.headers.items()]),
                        content=res.content
                    )
                    self.result.current_case.add_success(step.name, step.description, basic_output)
                except Exception:
                    logger.error(traceback.format_exc())
                    self.result.current_case.add_error(step.name, step.description, '', sys.exc_info())
                    continue
            else:  # run other step
                step_runner = StepRunner(step, self.scope)
                step_runner.run()
                self.scope = step_runner.final_scope()
                basic_output = """
Variable:%(variable)s
Expression:%(expression)s
Return Value: %(variable_value)s
""" % dict(
                    variable=step_runner.variable,
                    expression=step_runner.expression,
                    variable_value=step_runner.variable_value,
                    error='',)
                if not step_runner.error:
                    self.result.current_case.add_success(step.name, step.description, basic_output)  #
                else:
                    exc_name, exc_msg = step_runner.error[0].get_error()
                    if exc_name == settings.SMARTQC_FAILURE_EXCEPTION.__name__:
                        self.result.current_case.add_failure(step.name, step.description, basic_output,
                                                             'Exception:' + exc_msg)
                    else:
                        self.result.current_case.add_error(step.name, step.description, basic_output,
                                                           'Exception:' + exc_msg)
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
        self.error = []
        self.variable_value = None


    def run(self):
        input_modules = self.modules if self.modules else []
        self.scope.current_ns.update(self.scope.global_ns)
        self.scope.current_ns.update(self.scope.local_ns)
        self.scope.current_ns.update((m, __import__(m)) for m in input_modules if m)
        # self.scope.current_ns['assert_that'] = __import__('assertpy', globals(), locals(), [str('assert_that')])
        self.scope.current_ns.update(self.namespace)
        evaled = EvalExpression(self.expression, self.scope)
        self.expression, self.variable_value, self.error = evaled.evaluate()
        self.result[self.variable] = self.variable_value
        self.scope = evaled.scope
        logger.info("%s evaluate result is: %s %s" % (self.expression, type(self.variable_value), self.variable_value))

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
