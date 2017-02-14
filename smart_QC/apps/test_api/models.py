# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
REQUEST_METHODS = (
    ('GET', 'GET'),
    ('POST', 'POST'),
    ('DELETE', 'DELETE'),
    ('PUT', 'PUT'),
    ('HEAD', 'HEAD'),
    ('OPTIONS', 'OPTIONS'),
    ('TRACE', 'TRACE'),
)

ORIGINAL_API_STATUS = (
    (10, 'Not Analysed'),
    (11, 'Analysing'),
    (12, 'Analysed'),
    (22, 'Deleted'),
)

STATUS = (
    (10, 'Active'),
    (20, 'Disable'),
    (22, 'Deleted'),  # 逻辑删除
)

RUN_STATUS = (
    (0, 'Not Run'),
    (1, 'Running'),
    (2, 'FAILED'),
    (3, 'SUCCESS'),
)

CASE_TYPE = (
    (1, 'API'),
    (2, 'APIGroup'),
)

VAR_TYPE = (
    (1, 'Static'),
    (2, 'Evaluate'),
)

IS_DEFAULT = (
    (0, 'No'),
    (1, 'Yes'),
)


class ModuleHost(models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    hosts = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Module Host'
        verbose_name_plural = verbose_name


class OriginalAPI(models.Model):
    """
    原始接口数据模型（fiddler采集后导入的数据）
    """
    #
    module = models.ForeignKey(ModuleHost)
    # request
    method = models.CharField(max_length=10, choices=REQUEST_METHODS)
    url = models.URLField()
    protocol = models.CharField(max_length=10)
    host = models.CharField(max_length=30)
    path = models.FilePathField(max_length=30)
    params = models.TextField()  # params,headers,data are all saved with dict
    request_headers = models.TextField()
    data = models.TextField()
    # response
    status_code = models.IntegerField()
    response_headers = models.TextField()
    response_content = models.TextField()
    #
    create_time = models.DateTimeField(auto_now_add=True)
    status = models.SmallIntegerField(default=10, choices=ORIGINAL_API_STATUS)

    def __str__(self):
        return self.url

    class Meta:
        verbose_name = 'Original API'
        verbose_name_plural = verbose_name


class APITemplate(models.Model):
    """
    接口模板数据模型（使用api_md5字段区分唯一接口）
    """
    #
    name = models.CharField(max_length=40)
    original_api = models.ForeignKey(OriginalAPI)
    module = models.CharField(max_length=20)
    tags = models.CharField(max_length=60)
    # request
    method = models.CharField(max_length=10, choices=REQUEST_METHODS)
    url = models.URLField()
    protocol = models.CharField(max_length=10)
    host = models.CharField(max_length=30)
    path = models.FilePathField(max_length=30)
    params = models.TextField()  # params,headers,data are all saved with dict
    request_headers = models.TextField()
    data = models.TextField()
    # response
    status_code = models.IntegerField()
    response_headers = models.TextField()
    response_content = models.TextField()
    #
    create_time = models.DateTimeField(auto_now_add=True)
    modify_time = models.DateTimeField(auto_now=True)
    api_md5 = models.CharField(max_length=30)  # calculated by method, path, param keys, data keys
    status = models.SmallIntegerField(default=10, choices=STATUS)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'API Template'
        verbose_name_plural = verbose_name


class Case(models.Model):
    """
    接口用例数据模型
    """
    name = models.CharField(max_length=40)
    template = models.ForeignKey(APITemplate)
    # 来自模板信息，随模板更新
    module = models.CharField(max_length=20)
    tags = models.CharField(max_length=60)
    method = models.CharField(max_length=10, choices=REQUEST_METHODS)
    url = models.URLField()
    protocol = models.CharField(max_length=10)
    host = models.CharField(max_length=30)
    path = models.FilePathField(max_length=30)
    # 来自模板，但不随模板更新，支持参数化
    params = models.TextField()  # params,headers,data are all saved with dict
    request_headers = models.TextField()
    data = models.TextField()
    # 单独设置，支持参数化
    setup = models.TextField()
    teardown = models.TextField()
    #
    assertion_ids = models.CommaSeparatedIntegerField(max_length=30)  # 逗号分隔的断言id
    generated_var_ids = models.CommaSeparatedIntegerField(max_length=30)  # 关联生成的variable数据，执行后更新variable
    last_result_id = models.ForeignKey(RunningHistory)
    last_run_status = models.SmallIntegerField(default=0, choices=RUN_STATUS)
    status = models.SmallIntegerField(default=10, choices=STATUS)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Case'
        verbose_name_plural = verbose_name


class RunningHistory(models.Model):
    """
    用例执行结果历史，用于后续报告和统计分析。加入其他测试功能后可将此模块移至公共模块
    """
    # task = models.ForeignKey(Task)
    version = models.CharField(max_length=30)
    module = models.CharField(max_length=20)
    tags = models.CharField(max_length=60)
    case_type = models.SmallIntegerField(default=1, choices=CASE_TYPE)
    case_id = models.IntegerField()
    case_name = models.CharField(max_length=40)
    run_status = models.SmallIntegerField(default=0, choices=RUN_STATUS)
    fail_reason = models.CommaSeparatedIntegerField(max_length=30)
    detail = models.TextField()  # 用例运行详情，如果是单一接口测试，以json格式记录请求和返回，如果是接口组，则分别记录
    status = models.SmallIntegerField(default=10, choices=STATUS)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Case'
        verbose_name_plural = verbose_name


class CaseGroup(models.Model):
    """
    组合接口用例数据模型
    """
    name = models.CharField(max_length=40)
    invoke_case_ids = models.CommaSeparatedIntegerField(max_length=30)
    setup = models.TextField()
    teardown = models.TextField()
    #
    last_result_id = models.ForeignKey(RunningHistory)
    last_run_status = models.SmallIntegerField(default=0, choices=RUN_STATUS)
    status = models.SmallIntegerField(default=10, choices=STATUS)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'CaseGroup'
        verbose_name_plural = verbose_name


class Variable(models.Model):
    """
    参数化数据模型，借鉴RobotFramework参数化的方法，定义${},@{},&{}三种值类型的参数，借鉴evaluate关键字（eval方法）运行生成
    动态参数值，借鉴rf的find_var方法找到参数，并写一个装饰器处理用例运行过程中所有环节的参数化
    """
    name = models.CharField(max_length=40, primary_key=True)
    var_type = models.SmallIntegerField(default=1, choices=VAR_TYPE)  # var_type=1,表示直接取静态值
    expression = models.TextField()  # var_type=1时存入静态值，2时存入表达式
    modules = models.CharField(max_length=100)
    namespace = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Variable'
        verbose_name_plural = verbose_name


class Assertion(models.Model):
    """
    断言数据模型
    """
    name = models.CharField(max_length=40)
    case_type = models.SmallIntegerField(default=1, choices=CASE_TYPE)
    case_id = models.IntegerField()  # 0表示公共来源
    case_name = models.CharField(max_length=40)
    is_default = models.SmallIntegerField(default=0, choices=IS_DEFAULT)  # 1表示在用例没有关联断言时，运行默认断言

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Assertion'
        verbose_name_plural = verbose_name


# class PICTScript(models.Model):
#     """
#     在线生成或者上传pict(Pairwise Independent Combinatorial Testing tool)脚本，输出分析结果，用于自动生成测试用例
#     """
#     name = models.CharField(max_length=40)
#     in_put = models.TextField()
#     command = models.CharField(max_length=20)
#     out_put = models.TextField()




