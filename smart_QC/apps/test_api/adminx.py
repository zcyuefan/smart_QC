#!/usr/bin/env python
# encoding=utf-8
# Register your models here.
from __future__ import unicode_literals
import xadmin
from xadmin import views
# from models import TestHost, TestEnvironment, CaseTag, OriginalAPI, APITemplate, Case, ReplayLog, Variable, Assertion
from .models import TestHost, TestEnvironment, CaseTag, OriginalAPI, APITemplate, Case, Report, Step
from .forms import CaseAdminForm, StepAdminForm
from xadmin.layout import Main, TabHolder, Tab, Fieldset, Row, Side, PrependedAppendedText
from xadmin.plugins.inline import Inline
from xadmin.plugins.batch import BatchChangeAction
from .actions import RunCase, FailCase, BatchCopyAction
# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


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
    style_fields = {'hosts': 'm2m_transfer_with_help_text'}
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


class CaseAdmin(object):
    # exclude = []
    form = CaseAdminForm
    def list_display_options(self, instance):  # display list option
        # instance.last_run_status = '1'
        # instance.save()
        return "<a title = 'Run this case' onclick='alert(%s)'>" \
               "<i class='fa fa-play-circle fa-lg'></i></a>" % instance.id
    actions = [RunCase, FailCase, BatchChangeAction, BatchCopyAction]
    # batch_fields = [f.name for f in Case._meta.get_fields()]
    batch_fields = ['template', 'case_type', 'invoke_cases', 'description', 'tag', 'method', 'protocol',
                    'host', 'path', 'request_headers', 'params', 'data', 'step']
    style_fields = {'invoke_cases': 'sorted_m2m',
                    'tag': 'm2m_dropdown_with_help_text',
                    'step': 'sorted_m2m',
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
    list_display = ('id', 'name', 'case_type', 'invoke_cases', 'tag', 'method', 'protocol', 'host', 'path',
                    'last_run_status', 'list_display_options',)
    list_display_links = ('name',)
    readonly_fields = ('last_run_status',)
    search_fields = ('id', 'name', 'case_type', 'invoke_cases', 'tag', 'method', 'protocol', 'host', 'path',
                     'create_time', 'modify_time', 'last_run_status',)
    list_filter = ['id', 'name', 'case_type', 'invoke_cases', 'tag', 'method', 'protocol', 'host', 'path', 'request_headers', 'params',
                   'data', 'create_time', 'modify_time', 'last_run_status']
    # ('service_type', xadmin.filters.MultiSelectFieldListFilter)]

    list_bookmarks = []
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
                         Tab('API detail',
                             'method',
                             Row('protocol', 'host', ),
                             'path', 'request_headers', 'params', 'data',
                             ),
                         Tab('Running steps',
                             'step'
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


class ReportAdmin(object):
    # list_display = ('record_module', )
    list_select_related = True
    model_icon = 'fa fa-file'
    reversion_enable = True
    # actions = [BatchCopyAction, ]


class StepAdmin(object):
    form = StepAdminForm
    base_fields = ['name', 'usage', 'variable', 'global_scope', 'modules', 'namespace', 'expression', 'description', ]
    list_display = base_fields
    list_editable = base_fields
    search_fields = base_fields + ['create_time', 'modify_time',]
    list_filter = base_fields + ['create_time', 'modify_time',]
    list_select_related = True
    model_icon = 'fa fa-edit'
    reversion_enable = True
    actions = [BatchCopyAction, ]
    form_layout = (
        Main(Fieldset('', 'name', 'usage', Row(PrependedAppendedText('variable', '${', '}'), 'global_scope'), Row('modules', 'namespace', ), 'expression',
                      css_class='unsort short_label no_title')),
        Side(Fieldset('', 'description', css_class='unsort short_label no_title')))

xadmin.sites.site.register(TestHost, TestHostAdmin)
xadmin.sites.site.register(TestEnvironment, TestEnvironmentAdmin)
xadmin.sites.site.register(OriginalAPI, OriginalAPIAdmin)
xadmin.sites.site.register(APITemplate, APITemplateAdmin)
xadmin.sites.site.register(Case, CaseAdmin)
xadmin.sites.site.register(Report, ReportAdmin)
xadmin.sites.site.register(CaseTag, CaseTagAdmin)
xadmin.sites.site.register(Step, StepAdmin)