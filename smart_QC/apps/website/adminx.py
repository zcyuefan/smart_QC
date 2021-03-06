#!/usr/bin/env python
# encoding=utf-8
# Register your models here.
import xadmin
from xadmin import views
from models import IDC, Host, MaintainLog, HostGroup, AccessRecord
from xadmin.layout import Main, TabHolder, Tab, Fieldset, Row, Col, AppendedText, Side
from xadmin.plugins.inline import Inline
from xadmin.plugins.batch import BatchChangeAction
from xadmin.plugins.multiselect import M2MSelectPlugin, ManyToManyField, SelectMultipleTransfer, \
    SelectMultipleDropdown
from xadmin.views import BaseAdminPlugin, ModelFormAdminView
from sortedm2m.fields import SortedManyToManyField
from sortedm2m.forms import SortedCheckboxSelectMultiple

#  菜单还需要设置
# rtm（需求跟踪）：版本管理，原始需求，需求分解，测试要点，代码地图
# task任务管理：
# 接口测试：全局设置，原始接口，接口模板，单一接口用例，组合接口用例
# report（历史报表）：

class MainDashboard(object):
    widgets = [
        [
            {"type": "html", "title": "Test Widget",
             "content": "<h3> Welcome to 54324332322323232n! </h3><p>Join Online Group: <br/>QQ Qun : 000000000</p>"},
            {"type": "chart", "model": "website.accessrecord", 'chart': 'user_count',
             'params': {'_p_date__gte': '2013-01-08', 'p': 1, '_p_date__lt': '2013-01-29'}},
            {"type": "list", "model": "website.host", 'params': {
                'o': '-guarantee_date'}},
        ],
        [
            {"type": "qbutton", "title": "Quick Start",
             "btns": [{'model': Host}, {'model': IDC}, {'title': "Baidu", 'url': "http://www.baidu.com"}]},
            {"type": "addform", "model": MaintainLog},
        ]
    ]


xadmin.sites.site.register(views.website.IndexView, MainDashboard)


class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True


xadmin.sites.site.register(views.BaseAdminView, BaseSetting)


class GlobalSetting(object):
    global_search_models = [Host, IDC]
    global_models_icon = {
        Host: 'fa fa-laptop', IDC: 'fa fa-cloud'
    }
    site_title = 'Smart QC'
    site_footer = 'yuefan 2017'
    menu_style = 'accordion'  # 'accordion'


xadmin.sites.site.register(views.CommAdminView, GlobalSetting)


class M2MSelectPluginWithHelpText(M2MSelectPlugin):
    def init_request(self, *args, **kwargs):
        return hasattr(self.admin_view, 'style_fields') and \
            (
                'm2m_transfer_with_help_text' in self.admin_view.style_fields.values() or
                'm2m_dropdown_with_help_text' in self.admin_view.style_fields.values() or
                'sorted_m2m' in self.admin_view.style_fields.values()
            )

    def get_field_style(self, attrs, db_field, style, **kwargs):
        help_text = db_field.help_text if db_field.help_text else ""
        if style == 'm2m_transfer_with_help_text' and isinstance(db_field, ManyToManyField):
            return {'widget': SelectMultipleTransfer(db_field.verbose_name, False), 'help_text': help_text}
        if style == 'm2m_dropdown_with_help_text' and isinstance(db_field, ManyToManyField):
            return {'widget': SelectMultipleDropdown, 'help_text': help_text}
        if style == 'sorted_m2m' and isinstance(db_field, SortedManyToManyField):
            return {'widget': SortedCheckboxSelectMultiple, 'help_text': help_text}
        return attrs

xadmin.site.register_plugin(M2MSelectPluginWithHelpText, ModelFormAdminView)


class MaintainInline(object):
    model = MaintainLog
    extra = 1
    style = 'accordion'
    exclude = ['operator', 'note',]
    can_order = True
    ordering = ['-maintain_type',]

    # def has_add_permission(self):
    #     return True


class IDCAdmin(object):
    list_display = ('name', 'description', 'create_time')
    list_display_links = ('name',)
    wizard_form_list = [
        ('First\'s Form', ('name', 'description')),
        ('Second Form', ('contact', 'telphone', 'address')),
        ('Thread Form', ('customer_id',))
    ]

    search_fields = ['name']
    relfield_style = 'fk-select'
    reversion_enable = True

    actions = [BatchChangeAction, ]
    batch_fields = ('contact', 'groups')
    ordering = ('-name', )


class HostAdmin(object):
    def open_web(self, instance):
        return "<a href='http://%s' target='_blank'>Open</a>" % instance.ip

    open_web.short_description = "Acts"
    open_web.allow_tags = True
    open_web.is_column = True

    list_display = ('name', 'idc', 'guarantee_date', 'service_type',
                    'status', 'open_web', 'description')
    list_display_links = ('name',)

    raw_id_fields = ('idc',)
    style_fields = {'system': "radio-inline"}

    search_fields = ['name', 'ip', 'description']
    list_filter = ['idc', 'guarantee_date', 'status', 'brand', 'model',
                   'cpu', 'core_num', 'hard_disk', 'memory',
                   ('service_type', xadmin.filters.MultiSelectFieldListFilter)]

    list_quick_filter = ['service_type', {'field': 'idc__name', 'limit': 10}]
    list_bookmarks = [{'title': "Need Guarantee", 'query': {'status__exact': 2}, 'order': ('-guarantee_date',),
                       'cols': ('brand', 'guarantee_date', 'service_type')}]

    show_detail_fields = ('idc',)
    list_editable = (
        'name', 'idc', 'guarantee_date', 'service_type', 'description')
    save_as = True

    aggregate_fields = {"guarantee_date": "min"}
    grid_layouts = ('table', 'thumbnails')

    form_layout = (
        Main(
            TabHolder(
                Tab('Comm Fields',
                    Fieldset('Company data',
                             'name', 'idc',
                             description="some comm fields, required"
                             ),
                    Inline(MaintainLog),
                    ),
                Tab('Extend Fields',
                    Fieldset('Contact details',
                             'service_type',
                             Row('brand', 'model'),
                             Row('cpu', 'core_num'),
                             Row(AppendedText(
                                 'hard_disk', 'G'), AppendedText('memory', "G")),
                             'guarantee_date'
                             ),
                    ),
            ),
        ),
        Side(
            Fieldset('Status data',
                     'status', 'ssh_port', 'ip'
                     ),
        )
    )
    inlines = [MaintainInline]
    reversion_enable = True

    data_charts = {
        "host_service_type_counts": {'title': u"Host service type count", "x-field": "service_type",
                                     "y-field": ("service_type",),
                                     "option": {
                                         "series": {"bars": {"align": "center", "barWidth": 0.8, 'show': True}},
                                         "xaxis": {"aggregate": "count", "mode": "categories"},
                                     },
                                     },
    }


class HostGroupAdmin(object):
    list_display = ('name', 'description', 'hosts')
    list_display_links = ('name',)

    search_fields = ['name']
    style_fields = {'hosts': 'checkbox-inline'}
    from smart_QC.apps.test_api.actions import BatchCopyAction
    actions = [BatchCopyAction, ]


class MaintainLogAdmin(object):
    list_display = (
        'host', 'maintain_type', 'hard_type', 'time', 'operator', 'note', 'cpu')
    list_display_links = ('host',)

    def cpu(self, obj):
        return obj.host.cpu
    list_filter = ['host', 'maintain_type', 'hard_type', 'time', 'operator']
    search_fields = ['note']

    form_layout = (
        Col("col2",
            Fieldset('Record data',
                     'time', 'note',
                     css_class='unsort short_label no_title'
                     ),
            span=9, horizontal=True
            ),
        Col("col1",
            Fieldset('Comm data',
                     'host', 'maintain_type'
                     ),
            Fieldset('Maintain details',
                     'hard_type', 'operator'
                     ),
            span=3
            )
    )
    reversion_enable = True


class AccessRecordAdmin(object):
    def avg_count(self, instance):
        return int(instance.view_count / instance.user_count)

    avg_count.short_description = "Avg Count"
    avg_count.allow_tags = True
    avg_count.is_column = True

    list_display = ('date', 'user_count', 'view_count', 'avg_count')
    list_display_links = ('date',)

    list_filter = ['date', 'user_count', 'view_count']
    actions = None
    aggregate_fields = {"user_count": "sum", 'view_count': "sum"}

    refresh_times = (3, 5, 10)
    data_charts = {
        "user_count": {'title': u"User Report", "x-field": "date", "y-field": ("user_count", "view_count"),
                       "order": ('date',)},
        "avg_count": {'title': u"Avg Report", "x-field": "date", "y-field": ('avg_count',), "order": ('date',)},
        "per_month": {'title': u"Monthly Users", "x-field": "_chart_month", "y-field": ("user_count",),
                      "option": {
                          "series": {"bars": {"align": "center", "barWidth": 0.8, 'show': True}},
                          "xaxis": {"aggregate": "sum", "mode": "categories"},
                      },
                      },
    }

    def _chart_month(self, obj):
        return obj.date.strftime("%B")


xadmin.sites.site.register(Host, HostAdmin)
xadmin.sites.site.register(HostGroup, HostGroupAdmin)
xadmin.sites.site.register(MaintainLog, MaintainLogAdmin)
xadmin.sites.site.register(IDC, IDCAdmin)
xadmin.sites.site.register(AccessRecord, AccessRecordAdmin)
