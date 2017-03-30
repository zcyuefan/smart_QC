import xadmin
from djcelery.models import *
from .actions import EnableTasks, DisableTasks
from djcelery.admin import PeriodicTaskForm
from xadmin.layout import Main, Side, Fieldset


class TaskStateAdmin(object):
    model_icon = 'fa fa-tags'
    reversion_enable = True


class WorkerStateAdmin(object):
    model_icon = 'fa fa-tags'
    reversion_enable = True


class IntervalScheduleAdmin(object):
    model_icon = 'fa fa-spinner'
    reversion_enable = True


class CrontabScheduleAdmin(object):
    model_icon = 'glyphicon glyphicon-time'
    reversion_enable = True


class PeriodicTaskAdmin(object):
    form = PeriodicTaskForm
    displayed_list = [
        'enabled',
        '__unicode__',
        'task',
        'args',
        'kwargs',
    ]
    list_display = displayed_list
    list_editable = [i for i in displayed_list if i not in ['__unicode__']]
    list_display_links = ('__unicode__',)
    search_fields = ('name', '__unicode__', 'task')
    ordering = ('-enabled', 'name')
    list_filter = [i for i in displayed_list if i not in ['__unicode__']]
    list_select_related = True
    model_icon = 'fa fa-tasks'
    reversion_enable = True
    form_layout = (
        Main(
            Fieldset('Basic Fields',
                     'name', 'regtask', 'task', 'enabled',
                     ),
            Fieldset('Schedule',
                     'interval', 'crontab'
                     ),
            Fieldset('Arguments',
                     'args', 'kwargs'
                     ),
            ),
        Side(
            Fieldset('Execution Options',
                     'expires', 'queue', 'exchange', 'routing_key'
                     )
        )
    )
    actions = [EnableTasks, DisableTasks]


# Register your models here.
# xadmin.site.register(TaskState, TaskStateAdmin)
# xadmin.site.register(WorkerState, WorkerStateAdmin)
xadmin.site.register(IntervalSchedule, IntervalScheduleAdmin)
xadmin.site.register(CrontabSchedule, CrontabScheduleAdmin)
xadmin.site.register(PeriodicTask, PeriodicTaskAdmin)