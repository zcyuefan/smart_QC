# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from smart_QC.libs.json_field import JSONField
import ast
from sortedm2m.fields import SortedManyToManyField
from multiselectfield import MultiSelectField
from django.utils.translation import ugettext_lazy as _
# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

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


class BaseModel(models.Model):
    name = models.CharField(max_length=40, unique=True)
    description = models.TextField(max_length=255, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    modify_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class RequestModel(models.Model):
    method = models.CharField(max_length=10, choices=REQUEST_METHODS)
    protocol = models.CharField(default='https', max_length=10)
    host = models.ForeignKey('TestHost', to_field='name')
    path = models.CharField(max_length=255)
    # params,headers,data are all saved with dict
    params = JSONField(default='', blank=True, ignore_error=True, encoder_kwargs={'indent': 4, 'ensure_ascii': False})
    request_headers = JSONField(default='', blank=True, ignore_error=True,
                                encoder_kwargs={'indent': 4, 'ensure_ascii': False})
    data = JSONField(default='', blank=True, ignore_error=True, encoder_kwargs={'indent': 4, 'ensure_ascii': False})

    class Meta:
        abstract = True


class ResponseModel(models.Model):
    status_code = models.CharField(max_length=10, choices=STATUS_CODES)
    response_headers = JSONField(default='', blank=True, ignore_error=True,
                                 encoder_kwargs={'indent': 4, 'ensure_ascii': False})
    response_content = JSONField(default='', blank=True, ignore_error=True,
                                 encoder_kwargs={'indent': 4, 'ensure_ascii': False})

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
    (0, 'pass'),
    (1, 'fail'),
    (2, 'error'),
    (3, 'never run'),
)

STEP_USAGE = (
    (0, 'Common'),
    (1, 'Default assertion'),
    (2, 'Send request'),
)

class Step(BaseModel):
    """

    """
    usage = models.PositiveSmallIntegerField(default=0, choices=STEP_USAGE,
                                             help_text="""Help for particular choice item:
                                             <table id="id_usage_help" class="tablesorter table table-bordered table-striped table-hover">
                                                <thead>
                                                <tr>
                                                    <th>Your Choice</th>
                                                    <th>Help</th>
                                                </tr>
                                                </thead>
                                                <tbody>
                                                    <tr>
                                                        <td>Default assertion</td>
                                                        <td>e.g. assertion 200 response status</td>
                                                    </tr>
                                                     <tr>
                                                        <td>Send the request</td>
                                                        <td>Send request in case,fields below will be ignored if checked.</br>
                                                            For this choice, 1 object is enough!
                                                        </td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                               """)
    variable = models.CharField(max_length=70, blank=True, null=True, unique=True, default=None,
                                help_text="""Variable name to save result returned by
                                        expression evaluation. Syntax: ${variable}""")
    global_scope = models.BooleanField(default=False, help_text="Available to referenced by other case.")
    modules = MultiSelectField(choices=settings.EVAL_SAFE_MODULES,
                               null=True, blank=True,
                               help_text="Python modules to be imported and added to the evaluation namespace.")
    # modules = models.CharField(max_length=255, blank=True, help_text="""Used to specify a comma separated list of
    # Python modules to be imported and added to the evaluation namespace.""")
    namespace = models.CharField(max_length=255, blank=True, default='{}', help_text="""Used to pass a custom evaluation namespace
    as a dictionary. Possible ``modules`` are added to this namespace.""")
    expression = models.TextField(blank=True,
                                  help_text="""Python code to be evaluated,available variables:
                                               <table id="id_expression_help" class="tablesorter table table-bordered table-striped table-hover">
                                                <thead>
                                                <tr>
                                                    <th>Name</th>
                                                    <th>Type</th>
                                                    <th>Value</th>
                                                    <th>Usage</th>
                                                </tr>
                                                </thead>
                                                <tbody>
                                                    <tr>
                                                        <td>${response}</td>
                                                        <td>class 'requests.models.Response'</td>
                                                        <td>Response object</td>
                                                        <td>${response}.status_code,${response}.request,<br/>
                                                        ${response}.json(),${response}.content <br/>
                                                        Example expression: assert ${response}.status_code==200</td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                               """)

    def __str__(self):
        return self.name

    def clean(self):
        """
        Clean up blank fields to null
        """
        if self.variable == "" or (self.variable is not None and self.variable.strip() == ""):
            self.variable = None
        if self.usage == 2 and self.name != 'send_request':
            raise ValidationError('Send request must named as "send_request"!')
        if self.usage != 2 and self.name == 'send_request':
            raise ValidationError('Step name "send_request" is not allowed for none-send_request usage!')


    class Meta:
        verbose_name = 'Step'
        verbose_name_plural = verbose_name + 's'


def get_default_step():
    # resultquery = (models.Q(default_assertion=True) | models.Q(field1='val12'))
    return Step.objects.filter(usage__in=[2, 1])


class Case(BaseModel, RequestModel):
    """
    接口用例数据模型
    """
    #
    #
    # def default_script():
    #     return Script.objects.filter(default_teardown_script=True)

    case_type = models.SmallIntegerField(default=0, choices=CASE_TYPE)
    invoke_cases = SortedManyToManyField('self', symmetrical=False, blank=True)
    template = models.ForeignKey(APITemplate, blank=True, null=True)
    tag = models.ManyToManyField(CaseTag, blank=True)
    # params,request_headers,data,setup,teardown支持参数化
    step = SortedManyToManyField(Step, blank=True,
                                 default=get_default_step,
                                 help_text='')
    last_run_status = models.SmallIntegerField(default=3, choices=RUN_STATUS)

    # def __init__(self, *args, **kwargs):
    #     super(Case, self).__init__(*args, **kwargs)
    #     if not self.id:
    #         # self.teardown = Script.objects.filter(default_teardown_script=True)
    #         print(Script.objects.filter(default_teardown_script=True))

    def __str__(self):
        return self.name


    # def clean(self):
    #     """Make sure all managers are also members."""
        # setup = list(self.cleaned_data['setup'])
        # self.clean_fields()
        # print(self.cleaned_data)
        # for manager in self.cleaned_data['managers']:
        #     if manager not in members:
        #         members.append(manager)
        # self.cleaned_data['members'] = members
        # return self.cleaned_data


    class Meta:
        verbose_name = 'Case'
        verbose_name_plural = verbose_name + 's'

# from django.db.models.signals import post_save, pre_delete, m2m_changed
#
# def handle_flow(sender, instance, *args, **kwargs):
#     print(Case.setup.count())
#     print("Signal catched !")
#
# m2m_changed.connect(handle_flow, sender=Case.setup.through)

Case._meta.get_field('method').blank = True
Case._meta.get_field('protocol').blank = True
Case._meta.get_field('host').blank = True
Case._meta.get_field('host').null = True
Case._meta.get_field('path').blank = True


class Report(BaseModel):
    """
    用例执行结果报告，用于后续报告和统计分析。加入其他测试功能后可将此模块移至公共模块
    """
    # task = models.ForeignKey(Task)
    version = models.CharField(max_length=30, blank=True)
    start_time = models.DateTimeField(blank=True)
    duration = models.DurationField(blank=True)
    total = models.PositiveSmallIntegerField(blank=True)
    pass_count = models.PositiveSmallIntegerField(blank=True)
    fail_count = models.PositiveSmallIntegerField(blank=True)
    error_count = models.PositiveSmallIntegerField(blank=True)
    path = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Report'
        verbose_name_plural = verbose_name

# class PICTScript(models.Model):
#     """
#     在线生成或者上传pict(Pairwise Independent Combinatorial Testing tool)脚本，输出分析结果，用于自动生成测试用例
#     """
#     name = models.CharField(max_length=40)
#     in_put = models.TextField()
#     command = models.CharField(max_length=20)
#     out_put = models.TextField()
