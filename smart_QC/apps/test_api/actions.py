#!/usr/bin/env python
# encoding=utf-8

# Author zhangchao@jinwantai.com
# date:2017/3/29
# topic: 
# update: 

"""
file doc
"""

from xadmin.plugins.actions import BaseActionView
from django.utils.translation import ugettext as _


class RunCase(BaseActionView):

    # 这里需要填写三个属性
    action_name = "run_case"    #: 相当于这个 Action 的唯一标示, 尽量用比较针对性的名字
    description = _(u'Run selected %(verbose_name_plural)s')  #: 描述, 出现在 Action 菜单中, 可以使用 ``%(verbose_name_plural)s`` 代替 Model 的名字.

    model_perm = 'change'    #: 该 Action 所需权限
    icon = 'fa fa-play' # 显示图标
    # 而后实现 do_action 方法
    def do_action(self, queryset):
        # queryset 是包含了已经选择的数据的 queryset
        queryset.update(last_run_status='1')
        # for obj in queryset:
        #     # obj 的操作
        #     ...
        # # 返回 HttpResponse
        # return HttpResponse(...)


class FailCase(BaseActionView):
    action_name = "fail_case"    #: 相当于这个 Action 的唯一标示, 尽量用比较针对性的名字
    description = _(u'Fail selected %(verbose_name_plural)s')  #: 描述, 出现在 Action 菜单中, 可以使用 ``%(verbose_name_plural)s`` 代替 Model 的名字.

    model_perm = 'change'    #: 该 Action 所需权限
    icon = 'fa fa-repeat' # 显示图标

    def do_action(self, queryset):
        # queryset 是包含了已经选择的数据的 queryset
        queryset.update(last_run_status='0')