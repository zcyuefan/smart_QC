#!/usr/bin/env python
# encoding=utf-8

# Author zhangchao@jinwantai.com
# date:2017/3/29
# topic: 
# update: 

"""
file doc
"""

from xadmin.plugins.actions import BaseActionView, ACTION_CHECKBOX_NAME
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode
from django.template.response import TemplateResponse

from django.core.exceptions import PermissionDenied
from xadmin.views.base import filter_hook


class RunCase1(BaseActionView):

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


class RunCase(BaseActionView):

    action_name = "run_selected"
    description = _(u'Wahaha selected %(verbose_name_plural)s')

    model_perm = 'change'
    icon = 'fa fa-play'

    @filter_hook
    def update_models(self, queryset):
        n = queryset.count()
        if n:
            queryset.update(last_run_status='1')
            # 调用task 方法，进行异步请求
        #     if self.delete_models_batch:
        #         queryset.delete()
        #     else:
        #         for obj in queryset:
        #             obj.delete()
        #     self.message_user(_("Successfully deleted %(count)d %(items)s.") % {
        #         "count": n, "items": model_ngettext(self.opts, n)
        #     }, 'success')

    # @filter_hook
    def do_action(self, queryset):
        # Check that the user has delete permission for the actual model
        if not self.has_change_permission():
            raise PermissionDenied

        # using = router.db_for_write(self.model)

        # Populate execute_objects, a data structure of all related objects that
        # will also be deleted.
        # execute_objects, model_count, perms_needed, protected = get_deleted_objects(
        #     queryset, self.opts, self.user, self.admin_site, using)

        # The user has already confirmed the deletion.
        # Do the deletion and return a None to display the change list view again.
        if self.request.POST.get('post'):
            # if perms_needed:
            #     raise PermissionDenied
            self.update_models(queryset)
            # Return None to display the change list page again.
            return None

        if len(queryset) == 1:
            objects_name = force_unicode(self.opts.verbose_name)
        else:
            objects_name = force_unicode(self.opts.verbose_name_plural)

        # if perms_needed or protected:
        #     title = _("Cannot delete %(name)s") % {"name": objects_name}
        # else:
        title = _("Are you sure?")

        context = self.get_context()
        execute_objects = [2, 3]
        perms_needed = [1, 2]
        protected = [1, 2]
        # test_environments = [1, 2, 3]
        test_environments = [{'id': '1', 'name': 'trunk'}, {'id': '2', 'name': 'branch'}, {'id': '3', 'name': 'branch'}]
        context.update({
            "title": title,
            "objects_name": objects_name,
            "execute_objects": [execute_objects],
            'queryset': queryset,
            "perms_lacking": perms_needed,
            "protected": protected,
            "opts": self.opts,
            "app_label": self.app_label,
            'action_checkbox_name': ACTION_CHECKBOX_NAME,
            "test_environments": test_environments,
        })

        # Display the confirmation page
        return TemplateResponse(self.request, 'test_api/run_case_selected_confirm.html', context)
