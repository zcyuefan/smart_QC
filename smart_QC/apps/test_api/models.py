# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from smart_QC.libs.json_field import JSONField
from django.utils.translation import ugettext_lazy as _


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


class TimeStampedWithStatusModel(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    modify_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class RequestModel(models.Model):
    method = models.CharField(max_length=10, choices=REQUEST_METHODS)
    protocol = models.CharField(default='https', max_length=10)
    host = models.ForeignKey('TestHost', to_field='name')
    path = models.CharField(max_length=30)
    # params,headers,data are all saved with dict
    params = JSONField(blank=True, ignore_error=True, encoder_kwargs={'indent': 4, 'ensure_ascii': False})
    request_headers = JSONField(blank=True, ignore_error=True, encoder_kwargs={'indent': 4, 'ensure_ascii': False})
    data = JSONField(blank=True, ignore_error=True, encoder_kwargs={'indent': 4, 'ensure_ascii': False})

    class Meta:
        abstract = True


class ResponseModel(models.Model):
    status_code = models.PositiveIntegerField(blank=True)
    response_headers = JSONField(blank=True, ignore_error=True, encoder_kwargs={'indent': 4, 'ensure_ascii': False})
    response_content = JSONField(blank=True, ignore_error=True, encoder_kwargs={'indent': 4, 'ensure_ascii': False})

    class Meta:
        abstract = True


class TestHost(TimeStampedWithStatusModel):
    """
    api host
    """
    name = models.CharField(max_length=40, unique=True)
    module = models.CharField(max_length=20)
    remark = models.TextField(max_length=255, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Test Host'
        verbose_name_plural = verbose_name


class TestEnvironment(TimeStampedWithStatusModel):
    name = models.CharField(max_length=40, unique=True)
    hosts = models.ManyToManyField(TestHost)
    remark = models.TextField(max_length=255, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Test Environment'
        verbose_name_plural = verbose_name


class CaseTag(TimeStampedWithStatusModel):
    name = models.CharField(max_length=20, unique=True)
    remark = models.TextField(max_length=255, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Case Tag'
        verbose_name_plural = verbose_name


class OriginalAPI(TimeStampedWithStatusModel, RequestModel, ResponseModel):
    """
    原始接口数据模型（fiddler采集后导入的数据）
    """
    # request
    # response
    templated = models.BooleanField(default=False)  # false表示未进行模板化处理

    def __str__(self):
        return self.method + ' ' + self.protocol + '://' + self.host.name + '/' + self.path

    class Meta:
        verbose_name = 'Original API'
        verbose_name_plural = verbose_name


class APITemplate(TimeStampedWithStatusModel, RequestModel, ResponseModel):
    """
    接口模板数据模型（使用api_md5字段区分唯一接口）
    """
    #
    name = models.CharField(max_length=40, unique=True)
    original_api = models.ForeignKey(OriginalAPI)
    # request
    # response
    param_keys = models.CharField(max_length=255, blank=True)
    data_keys = models.CharField(max_length=255, blank=True)
    api_md5 = models.CharField(max_length=30)  # calculated by method, path, param keys, data keys

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'API Template'
        verbose_name_plural = verbose_name


CASE_TYPE = (
    (0, 'Single API'),
    (1, 'APIGroup'),
)


RUN_STATUS = (
    (0, 'Not Run'),
    (1, 'Running'),
    (2, 'FAILED'),
    (3, 'SUCCESS'),
)


class ReplayLog(TimeStampedWithStatusModel):
    """
    用例执行结果历史，用于后续报告和统计分析。加入其他测试功能后可将此模块移至公共模块
    """
    # task = models.ForeignKey(Task)
    name = models.CharField(max_length=40, unique=True)
    version = models.CharField(max_length=30, blank=True)
    run_status = models.SmallIntegerField(default=0, choices=RUN_STATUS)
    fail_reason = models.TextField(max_length=30, blank=True)
    detail = models.TextField(blank=True)  # 用例运行详情，如果是单一接口测试，以json格式记录请求和返回，如果是接口组，则分别记录
    replay_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Replay Log'
        verbose_name_plural = verbose_name


class Variable(TimeStampedWithStatusModel):
    """
    参数化数据模型，借鉴RobotFramework参数化的方法，定义${},@{},&{}三种值类型的参数，借鉴evaluate关键字（eval方法）运行生成
    动态参数值，借鉴rf的find_var方法找到参数，并写一个装饰器处理用例运行过程中所有环节的参数化
    """
    VAR_TYPE = (
        (1, 'Static'),
        (2, 'Evaluate'),
    )
    name = models.CharField(max_length=40, unique=True)
    var_type = models.SmallIntegerField(default=1, choices=VAR_TYPE)  # var_type=1,表示直接取静态值
    expression = models.TextField()  # var_type=1时存入静态值，2时存入表达式
    modules = models.CharField(max_length=100, blank=True)
    namespace = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Variable'
        verbose_name_plural = verbose_name


class Assertion(TimeStampedWithStatusModel):
    """
    断言数据模型
    """
    name = models.CharField(max_length=40, unique=True)
    is_default = models.BooleanField(default=False)  # True表示在用例没有关联断言时，运行默认断言

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Assertion'
        verbose_name_plural = verbose_name


class Case(TimeStampedWithStatusModel, RequestModel):
    """
    接口用例数据模型
    """
    name = models.CharField(max_length=40)
    case_type = models.SmallIntegerField(default=0, choices=CASE_TYPE)
    invoke_cases = models.ManyToManyField('self', symmetrical=False, blank=True)
    template = models.ForeignKey(APITemplate)
    tag = models.ManyToManyField(CaseTag)
    # params,request_headers,data,setup,teardown支持参数化
    setup = models.TextField(blank=True)
    teardown = models.TextField(blank=True)
    #
    assertions = models.ManyToManyField(Assertion, blank=True)  # 逗号分隔的断言id
    generated_vars = models.ManyToManyField(Variable,blank=True)  # 关联生成的variable数据，执行后更新variable
    last_run_status = models.SmallIntegerField(default=0, choices=RUN_STATUS)
    replay_logs = models.ManyToManyField(ReplayLog, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Case'
        verbose_name_plural = verbose_name


# class PICTScript(models.Model):
#     """
#     在线生成或者上传pict(Pairwise Independent Combinatorial Testing tool)脚本，输出分析结果，用于自动生成测试用例
#     """
#     name = models.CharField(max_length=40)
#     in_put = models.TextField()
#     command = models.CharField(max_length=20)
#     out_put = models.TextField()




