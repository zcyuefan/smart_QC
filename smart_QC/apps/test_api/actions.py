#!/usr/bin/env python
# encoding=utf-8

# Author zhangchao@jinwantai.com
# date:2017/3/29
# topic: 
# update: 

"""
file doc
"""
from __future__ import unicode_literals
from xadmin.plugins.actions import BaseActionView, ACTION_CHECKBOX_NAME
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode
from django.template.response import TemplateResponse

from django.core.exceptions import PermissionDenied
from xadmin.views.base import filter_hook

from models import TestEnvironment
from tasks import run_case
import json


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
    description = _(u'Run selected %(verbose_name_plural)s')

    model_perm = 'change'
    icon = 'fa fa-play'

    @filter_hook
    def update_models(self, queryset):
        n = queryset.count()
        if n:
            queryset.update(last_run_status='1')
            # 调用task 方法，进行异步请求
            arguments_str = self.request.POST.get('arguments', '')
            if arguments_str:
                try:
                    arguments_obj = json.loads(arguments_str)
                    selected_environment = arguments_obj.get('test_environment', '')
                    selected_case = arguments_obj.get('case', '')
                    if int(selected_environment.get('id')) and isinstance(selected_case, list):
                        run_case(test_environment=selected_environment, case=selected_case)
                        # run_case.delay(test_environment=selected_environment, case=selected_case)
                        self.message_user(_("Successfully add the task to running the %(count)d %(items)s.") % {
                            "count": n, "items": "case"
                        }, 'success')
                    else:
                        self.message_user(_('Invalid environment or case!'),
                                          'error')
                except Exception:
                    import traceback
                    print(traceback.format_exc())
                    self.message_user(_('Invalid arguments, please select valid test environment and case!'), 'error')
            else:
                self.message_user(_('Arguments field is required!'), 'error')
        #     if self.delete_models_batch:
        #         queryset.delete()
        #     else:
        #         for obj in queryset:
        #             obj.delete()

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
        title = _("Ready to running the selected cases?")

        test_environments = TestEnvironment.objects.all()

        context = self.get_context()
        execute_objects = [2, 3]

        context.update({
            "title": title,
            "objects_name": objects_name,
            "execute_objects": [execute_objects],
            'queryset': queryset,
            "opts": self.opts,
            "app_label": self.app_label,
            'action_checkbox_name': ACTION_CHECKBOX_NAME,
            "test_environments": test_environments,
        })

        # Display the confirmation page
        return TemplateResponse(self.request, 'test_api/run_case_selected_confirm.html', context)
