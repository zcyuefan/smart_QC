# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from smart_QC.libs.json_field import JSONField
from smart_QC.libs.model_tools import BaseModel, AbstractClassWithoutFieldsNamed as without
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

STATUS_CODES = (
    ('100', '100 Continue'),
    ('101', '101 Switching Protocols'),
    ('102', '102 Processing'),
    ('200', '200 OK'),
    ('201', '201 Created'),
    ('202', '202 Accepted'),
    ('203', '203 Non-Authoritative Information'),
    ('204', '204 No Content'),
    ('205', '205 Reset Content'),
    ('206', '206 Partial Content'),
    ('207', '207 Multi-Status'),
    ('300', '300 Multiple Choices'),
    ('301', '301 Moved Permanently'),
    ('302', '302 Move temporarily'),
    ('303', '303 See Other'),
    ('304', '304 Not Modified'),
    ('305', '305 Use Proxy'),
    ('306', '306 Switch Proxy'),
    ('307', '307 Temporary Redirect'),
    ('400', '400 Bad Request'),
    ('401', '401 Unauthorized'),
    ('402', '402 Payment Required'),
    ('403', '403 Forbidden'),
    ('404', '404 Not Found'),
    ('405', '405 Method Not Allowed'),
    ('406', '406 Not Acceptable'),
    ('407', '407 Proxy Authentication Required'),
    ('408', '408 Request Timeout'),
    ('409', '409 Conflict'),
    ('410', '410 Gone'),
    ('411', '411 Length Required'),
    ('412', '412 Precondition Failed'),
    ('413', '413 Request Entity Too Large'),
    ('414', '414 Request-URI Too Long'),
    ('415', '415 Unsupported Media Type'),
    ('416', '416 Requested Range Not Satisfiable'),
    ('417', '417 Expectation Failed'),
    ('421', '421 There are too many connections from your internet address'),
    ('422', '422 Unprocessable Entity'),
    ('423', '423 Locked'),
    ('424', '424 Failed Dependency'),
    ('425', '425 Unordered Collection'),
    ('426', '426 Upgrade Required'),
    ('449', '449 Retry With'),
    ('500', '500 Internal Server Error'),
    ('501', '501 Not Implemented'),
    ('502', '502 Bad Gateway'),
    ('503', '503 Service Unavailable'),
    ('504', '504 Gateway Timeout'),
    ('505', '505 HTTP Version Not Supported'),
    ('506', '506 Variant Also Negotiates'),
    ('507', '507 Insufficient Storage'),
    ('509', '509 Bandwidth Limit Exceeded'),
    ('510', '510 Not Extended'),
    ('600', '600 Unparseable Response Headers'),
)


class RequestModel(models.Model):
    method = models.CharField(max_length=10, choices=REQUEST_METHODS)
    protocol = models.CharField(default='https', max_length=10)
    host = models.ForeignKey('TestHost', to_field='name')
    path = models.CharField(max_length=30)
    # params,headers,data are all saved with dict
    params = JSONField(default='', blank=True, ignore_error=True, encoder_kwargs={'indent': 4, 'ensure_ascii': False})
    request_headers = JSONField(default='', blank=True, ignore_error=True, encoder_kwargs={'indent': 4, 'ensure_ascii': False})
    data = JSONField(default='', blank=True, ignore_error=True, encoder_kwargs={'indent': 4, 'ensure_ascii': False})

    class Meta:
        abstract = True


class ResponseModel(models.Model):
    status_code = models.CharField(max_length=10, choices=STATUS_CODES)
    response_headers = JSONField(default='', blank=True, ignore_error=True, encoder_kwargs={'indent': 4, 'ensure_ascii': False})
    response_content = JSONField(default='', blank=True, ignore_error=True, encoder_kwargs={'indent': 4, 'ensure_ascii': False})

    class Meta:
        abstract = True


class TestHost(BaseModel):
    """
    api host
    """
    module = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Test Host'
        verbose_name_plural = verbose_name + 's'


class TestEnvironment(BaseModel):
    hosts = models.ManyToManyField(TestHost)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Test Environment'
        verbose_name_plural = verbose_name


class CaseTag(BaseModel):
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Case Tag'
        verbose_name_plural = verbose_name + 's'


class OriginalAPI(BaseModel, RequestModel, ResponseModel):
    """
    原始接口数据模型（fiddler采集后导入的数据）
    """
    # name = models.CharField(max_length=40, blank=True)
    # request
    # response
    templated = models.BooleanField(default=False)  # false表示未进行模板化处理

    def __str__(self):
        return self.method + ' ' + self.protocol + '://' + self.host.name + '/' + self.path

    class Meta:
        verbose_name = 'Original API'
        verbose_name_plural = verbose_name
OriginalAPI._meta.get_field('name').blank = True


class APITemplate(BaseModel, RequestModel, ResponseModel):
    """
    接口模板数据模型（使用api_md5字段区分唯一接口）
    """
    #
    original_api = models.ForeignKey(OriginalAPI, blank=True)
    # request
    # response
    param_keys = models.CharField(max_length=255, blank=True)
    data_keys = models.CharField(max_length=255, blank=True)
    api_md5 = models.CharField(max_length=30)  # calculated by method, path, param keys, data keys

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'API Template'
        verbose_name_plural = verbose_name + 's'


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


class Variable(BaseModel):
    """
    参数化数据模型，借鉴RobotFramework参数化的方法，定义${},@{},&{}三种值类型的参数，借鉴evaluate关键字（eval方法）运行生成
    动态参数值，借鉴rf的find_var方法找到参数，并写一个装饰器处理用例运行过程中所有环节的参数化
    """
    VAR_TYPE = (
        (1, 'Static'),
        (2, 'Evaluate'),
    )
    var_type = models.SmallIntegerField(default=1, choices=VAR_TYPE)  # var_type=1,表示直接取静态值
    expression = models.TextField()  # var_type=1时存入静态值，2时存入表达式
    modules = models.CharField(max_length=100, blank=True)
    namespace = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Variable'
        verbose_name_plural = verbose_name + 's'


class Assertion(BaseModel):
    """
    断言数据模型
    """
    is_default = models.BooleanField(default=False)  # True表示在用例没有关联断言时，运行默认断言

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Assertion'
        verbose_name_plural = verbose_name + 's'


class Case(BaseModel, RequestModel):
    """
    接口用例数据模型
    """
    case_type = models.SmallIntegerField(default=0, choices=CASE_TYPE)
    invoke_cases = models.ManyToManyField('self', symmetrical=False, blank=True)
    template = models.ForeignKey(APITemplate, blank=True, null=True)
    tag = models.ManyToManyField(CaseTag, blank=True)
    # params,request_headers,data,setup,teardown支持参数化
    setup = models.TextField(blank=True, help_text='Python code to run before sending the request.')
    teardown = models.TextField(blank=True, help_text='Python code to run after request sent.')
    #
    assertions = models.ManyToManyField(Assertion, blank=True)  # 逗号分隔的断言id
    generated_vars = models.ManyToManyField(Variable, blank=True)  # 关联生成的variable数据，执行后更新variable
    last_run_status = models.SmallIntegerField(default=0, choices=RUN_STATUS)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Case'
        verbose_name_plural = verbose_name + 's'

Case._meta.get_field('method').blank = True
Case._meta.get_field('protocol').blank = True
Case._meta.get_field('host').blank = True
Case._meta.get_field('host').null = True
Case._meta.get_field('path').blank = True


class ReplayLog(models.Model):
    """
    用例执行结果历史，用于后续报告和统计分析。加入其他测试功能后可将此模块移至公共模块
    """
    # task = models.ForeignKey(Task)
    case = models.ForeignKey(Case)
    version = models.CharField(max_length=30, blank=True)
    run_status = models.SmallIntegerField(default=0, choices=RUN_STATUS)
    fail_reason = models.TextField(max_length=30, blank=True)
    detail = models.TextField(blank=True)  # 用例运行详情，如果是单一接口测试，以json格式记录请求和返回，如果是接口组，则分别记录
    replay_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '[%s] [%s] [%s] [%s]' % (self.version, self.case.name,
                                      self.replay_time.strftime('%Y-%m-%d %H:%M:%S'), RUN_STATUS[self.run_status][1],)

    class Meta:
        verbose_name = 'Replay Log'
        verbose_name_plural = verbose_name
# class PICTScript(models.Model):
#     """
#     在线生成或者上传pict(Pairwise Independent Combinatorial Testing tool)脚本，输出分析结果，用于自动生成测试用例
#     """
#     name = models.CharField(max_length=40)
#     in_put = models.TextField()
#     command = models.CharField(max_length=20)
#     out_put = models.TextField()




