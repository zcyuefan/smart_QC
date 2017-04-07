#!/usr/bin/env python
# encoding=utf-8
# Register your models here.
import xadmin
from xadmin import views
from models import TestHost, TestEnvironment, CaseTag, OriginalAPI, APITemplate, Case, ReplayLog, Variable, Assertion
from xadmin.layout import Main, TabHolder, Tab, Fieldset, Row, Col, AppendedText, Side
from xadmin.plugins.inline import Inline
# from xadmin.plugins.batch import BatchChangeAction
from actions import RunCase, FailCase
# from tasks import add
# add.delay(2, 2)


class TestHostAdmin(object):
    list_display = ('name', 'module', 'description')
    list_display_links = ('name',)

    search_fields = ['name', 'module', 'description', 'default_host', ]
    model_icon = 'fa fa-laptop'
    list_editable = ('name', 'module', 'description')
    list_select_related = True
    reversion_enable = True
    actions_on_top = False


class TestEnvironmentAdmin(object):
    list_display = ('name', 'hosts', 'description', )
    list_display_links = ('name',)
    search_fields = ['name', 'hosts', 'description', 'default_host', ]
    # style_fields = {'hosts': 'checkbox-inline'}
    style_fields = {'hosts': 'm2m_transfer'}
    model_icon = 'fa fa-cloud'
    list_editable = ('name', 'hosts', 'description', )
    list_select_related = True
    reversion_enable = True


class CaseTagAdmin(object):
    list_display = ('name', 'description', )
    list_display_links = ('name',)
    search_fields = ['name', 'description', ]
    list_editable = ('name', 'description', )
    raw_id_fields = ('Case',)
    list_select_related = True
    model_icon = 'fa fa-tags'
    reversion_enable = True


class OriginalAPIAdmin(object):
    def list_display_options(self, instance):
        return "<a href='http://%s' target='_blank'>Open</a>" % instance.url
    list_display_options.short_description = "options"
    list_display_options.allow_tags = True
    list_display_options.is_column = True
    refresh_times = (3, 5)
    list_editable = ('status_code', 'method', 'protocol', 'host', 'path', 'templated')
    list_display = ('id', 'status_code', 'method', 'protocol', 'host', 'path', 'templated',
                    'create_time', 'modify_time', 'list_display_options', )
    list_display_links = ('id',)

    search_fields = ('id', 'status_code', 'method', 'protocol', 'host', 'path', 'templated',
                     'create_time', 'modify_time',)
    list_filter = ['id', 'status_code', 'method', 'protocol', 'host', 'path', 'templated',
                   'create_time', 'modify_time',]
                   # ('service_type', xadmin.filters.MultiSelectFieldListFilter)]

    list_bookmarks = [{'title': "Need handle", 'query': {'is_handled': 0}, 'order': ('-modify_time',),
                       'cols': ('id', 'status_code', 'method', 'protocol', 'host', 'path',
                                'create_time', 'modify_time',)}]
    form_layout = (
        Fieldset("Common Fields",
                 'method',
                 Row('protocol', 'host', 'path',),
                 'templated',
                 # horizontal=True,
                 ),
        Fieldset('Extend Fields',
                 TabHolder(
                     Tab('Request',
                         'request_headers', 'params', 'data',
                         ),
                     Tab('Response',
                         'response_headers', 'status_code', 'response_content',
                         ),
                    ),
                 ),
    )

    reversion_enable = True
    list_select_related = True
    # show_detail_fields = ('host',)


class APITemplateAdmin(object):
    def list_display_options(self, instance):
        return "<a href='http://%s' target='_blank'>Open</a>" % instance.url
    list_display_options.short_description = "options"
    list_display_options.allow_tags = True
    list_display_options.is_column = True
    list_select_related = True
    model_icon = 'fa fa-leaf'
    reversion_enable = True
    list_editable = ('name', 'status_code', 'method', 'protocol', 'host', 'path', 'request_headers', 'params',  'data',)
    refresh_times = (3, 5)
    list_display = ('id', 'name', 'status_code', 'method', 'protocol', 'host', 'path', 'request_headers', 'params',
                    'data', 'create_time', 'modify_time', 'list_display_options', )
    list_display_links = ('name',)
    readonly_fields = ('api_md5',)
    search_fields = ('id', 'name', 'status_code', 'method', 'protocol', 'host', 'path',
                     'create_time', 'modify_time', )
    list_filter = ['id', 'name', 'status_code', 'method', 'protocol', 'host', 'path', 'request_headers', 'params',
                   'data', 'api_md5', 'create_time', 'modify_time', ]
                   # ('service_type', xadmin.filters.MultiSelectFieldListFilter)]

    list_bookmarks = []
    form_layout = (
        Fieldset("Common Fields",
                 'name', 'original_api', 'method',
                 Row('protocol', 'host', 'path',),
                 # horizontal=True,
                 ),
        Fieldset('Extend Fields',
                 TabHolder(
                     Tab('Request',
                         'request_headers', 'params', 'data',
                         ),
                     Tab('Response',
                         'response_headers', 'status_code', 'response_content',
                         ),
                        ),
                 ),
    )


class ReplayInline(object):
    model = ReplayLog
    extra = 1
    style = 'accordion'


class CaseAdmin(object):
    def list_display_options(self, instance):  # display list option
        # instance.last_run_status = '1'
        # instance.save()
        return "<a title = 'Run this case' onclick='alert(%s)'>" \
               "<i class='fa fa-play-circle fa-lg'></i></a>" % instance.id

    # def run_case(self, request, queryset):  # 批量运行action django admin自身的方法
    #     queryset.update(last_run_status='1')  # 设置用例状态为执行中
    #     # 调用异步任务，进行接口回放
    #     # for obj in queryset:
    #     #     print(obj.template)
    #     #     from time import sleep
    #     #     # sleep(5)

    # run_case.short_description = "Run selected Case"
    # run_case.icon = 'fa fa-play'

    actions = [RunCase, FailCase]

    style_fields = {'invoke_cases': 'm2m_transfer',
                    'tag': 'm2m_transfer',
                    'assertions': 'm2m_transfer',
                    'generated_vars': 'm2m_transfer'
                    }
    list_display_options.short_description = "options"
    list_display_options.allow_tags = True
    list_display_options.is_column = True
    list_select_related = True
    # list_display = ('record_module', )
    model_icon = 'fa fa-code'
    reversion_enable = True
    list_editable = ('name', 'case_type', 'method', 'protocol', 'host', 'path', 'request_headers', 'params',  'data',)
    refresh_times = (3, 5)
    list_display = ('id', 'name', 'case_type', 'invoke_cases', 'tag', 'method', 'protocol', 'host', 'path', 'request_headers', 'params',
                    'data', 'last_run_status', 'list_display_options',)
    list_display_links = ('name',)
    readonly_fields = ('last_run_status',)
    search_fields = ('id', 'name', 'case_type', 'invoke_cases', 'tag', 'method', 'protocol', 'host', 'path',
                     'create_time', 'modify_time', 'last_run_status',)
    list_filter = ['id', 'name', 'case_type', 'invoke_cases', 'tag', 'method', 'protocol', 'host', 'path', 'request_headers', 'params',
                   'data', 'create_time', 'modify_time', 'last_run_status']
    # ('service_type', xadmin.filters.MultiSelectFieldListFilter)]

    list_bookmarks = []
    inlines = [ReplayInline]
    form_layout = (
        Main(
            Fieldset("Common Fields",
                     Row('name', 'last_run_status', ),
                     Row('case_type', 'template', ),
                     'invoke_cases',
                     # Row('protocol', 'host', 'path', ),
                     # horizontal=True,
                     ),
            Fieldset('Extend Fields',
                     TabHolder(
                         Tab('About case',
                             'description', 'tag',
                             ),
                         Tab('Pre Replay',
                             'setup',
                             ),
                         Tab('API detail',
                             'method',
                             Row('protocol', 'host', ),
                             'path', 'request_headers', 'params', 'data',
                             ),
                         Tab('Post Replay',
                             'assertions', 'generated_vars', 'teardown',
                             ),
                     ),
                     ),
        ),
        Side(
            # Fieldset('API Replay History',
            #          Inline(ReplayLog),
            #          ),
        )
    )
        # Fieldset("Common Fields",
        #          Row('name', 'last_run_status',),
        #          Row('case_type', 'template',),
        #          'invoke_cases',
        #          # Row('protocol', 'host', 'path', ),
        #          # horizontal=True,
        #          ),
        # Fieldset('Extend Fields',
        #          TabHolder(
        #              Tab('About case',
        #                  'description', 'tag',
        #                  ),
        #              Tab('Pre Replay',
        #                  'setup',
        #                  ),
        #              Tab('API detail',
        #                  'method',
        #                  Row('protocol', 'host', 'path', ),
        #                  'request_headers', 'params', 'data',
        #                  ),
        #              Tab('Post Replay',
        #                  'assertions', 'generated_vars', 'teardown',
        #                  ),
        #          ),
        #          ),
    # )


class ReplayLogAdmin(object):
    # list_display = ('record_module', )
    list_select_related = True
    model_icon = 'fa fa-file'
    reversion_enable = True


class VariableAdmin(object):
    # list_display = ('record_module', )
    list_select_related = True
    model_icon = 'fa fa-edit'
    reversion_enable = True


class AssertionAdmin(object):
    # list_display = ('record_module', )
    list_select_related = True
    model_icon = 'fa fa-check'
    reversion_enable = True

xadmin.sites.site.register(TestHost, TestHostAdmin)
xadmin.sites.site.register(TestEnvironment, TestEnvironmentAdmin)
xadmin.sites.site.register(OriginalAPI, OriginalAPIAdmin)
xadmin.sites.site.register(APITemplate, APITemplateAdmin)
xadmin.sites.site.register(Case, CaseAdmin)
xadmin.sites.site.register(ReplayLog, ReplayLogAdmin)
xadmin.sites.site.register(CaseTag, CaseTagAdmin)
xadmin.sites.site.register(Variable, VariableAdmin)
xadmin.sites.site.register(Assertion, AssertionAdmin) 