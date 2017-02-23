#!/usr/bin/env python
# encoding=utf-8
# Register your models here.
import xadmin
from xadmin import views
from models import TestHost, TestEnvironment, CaseTag, OriginalAPI, APITemplate, Case, ReplayLog, Variable, Assertion
from xadmin.layout import Main, TabHolder, Tab, Fieldset, Row, Col, AppendedText, Side
from xadmin.plugins.inline import Inline
# from xadmin.plugins.batch import BatchChangeAction


class TestHostAdmin(object):
    list_display = ('name', 'module', 'remark')
    list_display_links = ('name',)

    search_fields = ['name', 'module', 'remark', 'default_host', ]
    model_icon = 'fa fa-laptop'
    list_editable = ('name', 'module', 'remark')
    list_select_related = True
    reversion_enable = True


class TestEnvironmentAdmin(object):
    list_display = ('name', 'hosts', 'remark', )
    list_display_links = ('name',)
    search_fields = ['name', 'hosts', 'remark', 'default_host', ]
    # style_fields = {'hosts': 'checkbox-inline'}
    style_fields = {'hosts': 'm2m_transfer'}
    model_icon = 'fa fa-cloud'
    list_editable = ('name', 'hosts', 'remark', )
    list_select_related = True
    reversion_enable = True


class CaseTagAdmin(object):
    list_display = ('name', 'remark', )
    list_display_links = ('name',)
    search_fields = ['name', ]
    list_editable = ('name', 'remark', )
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
        TabHolder(
            Tab('tab1',
                Fieldset('Request',
                         'request_headers', 'params', 'data',
                         ),
                span=9, horizontal=True
                ),
            Tab('tab2',
                Fieldset('Response',
                         'response_headers', 'status_code', 'response_content',
                         ),
                span=3
                ),
        ),
    )

    reversion_enable = True
    list_select_related = True
    # show_detail_fields = ('host',)


class APITemplateAdmin(object):
    # list_display = ('record_module', )
    list_select_related = True
    model_icon = 'fa fa-leaf'
    reversion_enable = True


class CaseAdmin(object):
    # list_display = ('record_module', )
    list_select_related = True
    model_icon = 'fa fa-code'
    reversion_enable = True


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