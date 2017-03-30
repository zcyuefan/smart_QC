#!/usr/bin/env python
# encoding=utf-8

# Author zhangchao@jinwantai.com
# date:2017/3/30
# topic: 
# update: 

"""
file doc
"""
from xadmin.plugins.actions import BaseActionView
from django.utils.translation import ugettext as _


class EnableTasks(BaseActionView):

    # 这里需要填写三个属性
    action_name = "enable_tasks"    #: 相当于这个 Action 的唯一标示, 尽量用比较针对性的名字
    description = _(u'Enable selected %(verbose_name_plural)s')  #: 描述, 出现在 Action 菜单中, 可以使用 ``%(verbose_name_plural)s`` 代替 Model 的名字.

    model_perm = 'change'    #: 该 Action 所需权限
    icon = 'fa fa-check-circle' # 显示图标
    # 而后实现 do_action 方法

    def do_action(self, queryset):
        queryset.update(enabled=True)


class DisableTasks(BaseActionView):
    action_name = "disable_tasks"    #: 相当于这个 Action 的唯一标示, 尽量用比较针对性的名字
    description = _(u'Disable selected %(verbose_name_plural)s')  #: 描述, 出现在 Action 菜单中, 可以使用 ``%(verbose_name_plural)s`` 代替 Model 的名字.

    model_perm = 'change'    #: 该 Action 所需权限
    icon = 'fa fa-times-circle' # 显示图标

    def do_action(self, queryset):
        # queryset 是包含了已经选择的数据的 queryset
        queryset.update(enabled=False)