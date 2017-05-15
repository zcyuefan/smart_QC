# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from smart_QC.libs.json_field import JSONField
import ast
from sortedm2m.fields import SortedManyToManyField
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
    (0, 'Not Run'),
    (1, 'Running'),
    (2, 'FAILED'),
    (3, 'SUCCESS'),
)


class Script(BaseModel):
    """

    """
    default_teardown_script = models.BooleanField(default=False,
                                                  help_text="Default running script, e.g. assertion 200 response status"
                                                  )
    variable = models.CharField(max_length=70, blank=True, null=True, unique=True, default=None,
                                help_text="""Variable name to save result returned by
                                        expression evaluation. Syntax: ${variable}""")
    global_scope = models.BooleanField(default=False, help_text="Available to referenced by other case.")
    modules = models.CharField(max_length=255, blank=True, help_text="""Used to specify a comma separated list of
    Python modules to be imported and added to the evaluation namespace.""")
    namespace = models.CharField(max_length=255, blank=True, default='{}', help_text="""Used to pass a custom evaluation namespace
    as a dictionary. Possible ``modules`` are added to this namespace.Syntax: ${variable.namespace}""")
    expression = models.TextField(blank=True, help_text="Expression in Python to be evaluated.")

    def __str__(self):
        return self.name

    def clean(self):
        """
        Clean up blank fields to null
        """
        if self.variable == "" or (self.variable is not None and self.variable.strip() == ""):
            self.variable = None
        safe_modules = settings.EVAL_SAFE_MODULES
        if isinstance(self.modules, unicode):
            input_modules = self.modules.replace(' ', '').split(',') if self.modules else []
        else:
            raise ValidationError('modules is not string')
        if isinstance(self.namespace, unicode):
            try:
                ast.literal_eval(self.namespace)
            except Exception as e:
                raise ValidationError('Namespace SyntaxError: ' + str(e))
        else:
            raise ValidationError('namespace is not string')
        unsafe_modules = list(set(input_modules).difference(set(safe_modules)))
        if unsafe_modules:
            raise ValidationError('Unsafe module(s): %s' % ','.join(unsafe_modules))
        #
        ns = ast.literal_eval(self.namespace)
        a={"ee":2222,"gg":33}
        ns.update((m, __import__(m)) for m in input_modules if m)
        print(ns)
        ns.update(a)
        print(ns)
        from asteval import Interpreter
        aeval = Interpreter()
        aeval.symtable.update(ns)
        b=aeval('random.randint(1,ee)')
        print(b)

    def evaluate(self):
        """Evaluates the given code in Python and returns the results.

        ``code`` is evaluated in Python as explained in `Evaluating
        codes`.

        ``modules`` argument can be used to specify a comma separated
        list of Python modules to be imported and added to the evaluation
        namespace.

        ``namespace`` argument can be used to pass a custom evaluation
        namespace as a dictionary. Possible ``modules`` are added to this
        namespace. This is a new feature in Robot Framework 2.8.4.
        """
        # if isinstance(self.code, str) and '$' in self.code:
        #     self.code, variables = handle_variables_in_expression(self.code)
        # else:
        #     variables = {}
        self.code, variables = handle_variables_in_expression(self.code)
        self.namespace = self._create_evaluation_namespace()
        try:
            if not isinstance(self.code, str):
                raise TypeError("Code must be string, got %s."
                                % self._type_name(self.code))
            if not self.code:
                raise ValueError("Code cannot be empty.")
            return eval(self.code, self.namespace, variables)
        except:
            raise RuntimeError("Evaluating code '%s' failed"
                               % self.code)

    def _type_name(self, item):
        cls = item.__class__ if hasattr(item, '__class__') else type(item)
        named_types = {str: 'string', bool: 'boolean', int: 'integer',
                       type(None): 'None', dict: 'dictionary', type: 'class'}
        return named_types.get(cls, cls.__name__)

    def _handle_variables_in_code(self):
        pass

    def _create_evaluation_namespace(self):
        self.namespace = dict(self.namespace or {})
        self.modules = self.modules.replace(' ', '').split(',') if self.modules else []
        self.namespace.update((m, __import__(m)) for m in self.modules if m)
        return self.namespace

    class Meta:
        verbose_name = 'Script'
        verbose_name_plural = verbose_name + 's'


def handle_variables_in_expression(expression):
    if isinstance(expression, str) and '$' in expression:
        expression, variables = handle_variables_in_expression(expression)
    else:
        variables = {}
    return expression, variables


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
    setup = SortedManyToManyField(Script, blank=True, related_name="setup_set",
                                  help_text='Scripts running before sending the request, e.g. set variable, prepare test environment.')
    teardown = SortedManyToManyField(Script, blank=True, related_name="teardown_set",
                                     # default=default_script,
                                     help_text='Scripts running after request sent, e.g. set global variable, asserting, clear test environment')
    # setup = models.ManyToManyField(Script, blank=True, related_name="setup_set",
    #                                help_text='Scripts running before sending the request, e.g. set variable, prepare test environment.')
    # teardown = models.ManyToManyField(Script, blank=True, related_name="teardown_set",
    #                                   default=Script.objects.filter(default_teardown_script=True),
    #                                   help_text='Scripts running after request sent, e.g. set global variable, asserting, clear test environment')
    # # teardown = models.ManyToManyField(Script, through='CaseTeardownScript', blank=True,
    #                                   default=Script.objects.filter(default_teardown_script=True),
    #                                   help_text='Scripts running after request sent, e.g. set global variable, asserting, clear test environment')
    last_run_status = models.SmallIntegerField(default=0, choices=RUN_STATUS)

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


class CaseTeardownScript(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE)
    script = models.ForeignKey(Script, on_delete=models.CASCADE)
    rank = models.PositiveIntegerField()
    #
    # class Meta:
    #     ordering = ('number',)


class CaseSetupScript(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE)
    script = models.ForeignKey(Script, on_delete=models.CASCADE)
    rank = models.PositiveIntegerField()
    #
    # class Meta:
    #     ordering = ('number',)


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
