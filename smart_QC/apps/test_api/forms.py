#!/usr/bin/env python
# encoding=utf-8

# Author zhangchao@jinwantai.com
# date:2017/5/12
# topic: 
# update: 

"""
file doc
"""
from __future__ import unicode_literals
from django import forms
from django.core.exceptions import ValidationError
from .models import Case,Step
from xadmin.plugins.multiselect import SelectMultipleDropdown
# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Generates a function that sequentially calls the two functions that were
# passed to it
# def func_concat(old_func, new_func):
#     def function():
#         old_func()
#         new_func()
#     return function


# A dummy widget to be replaced with your own.
# class OrderedManyToManyWidget(forms.widgets.TextInput):
#     pass


# # A simple CharField that shows a comma-separated list of contestant IDs.
# class ResultsField(forms.CharField):
#     widget = OrderedManyToManyWidget()


class StepAdminForm(forms.ModelForm):
    class Meta:
        model = Step
        widgets = {
            # 'modules': forms.CheckboxSelectMultiple,
            'modules': SelectMultipleDropdown,
        }
        exclude = []


class CaseAdminForm(forms.ModelForm):
    # results = ResultsField()


    class Meta:
        model = Case
        exclude = []

    def clean(self):
        if self.cleaned_data.get('case_type') == 0 and 2 not in [step.usage for step in self.cleaned_data.get('step')]:
            raise ValidationError('Single API case must contains "send_request" in running steps!')

    # Override init so we can populate the form field with the existing data.
    # def __init__(self, *args, **kwargs):
    #     instance = kwargs.get('instance', None)
    #     # See if we are editing an existing case. If not, there is nothing
    #     # to be done.
    #     if instance and instance.pk:
    #         # Get a list of all the IDs of the scripts already specified
    #         # for this case.
    #         scripts = CaseSetupScript.objects.filter(case=instance).order_by('rank').values_list('script', flat=True)
    #         # Make them into a comma-separated string, and put them in our
    #         # custom field.
    #         self.base_fields['results'].initial = ','.join(map(str, scripts))
    #         # Depending on how you've written your widget, you can pass things
    #         # like a list of available scripts to it here, if necessary.
    #     super(CaseAdminForm, self).__init__(*args, **kwargs)
    #
    # def save(self, *args, **kwargs):
    #     # This "commit" business complicates things somewhat. When true, it
    #     # means that the model instance will actually be saved and all is
    #     # good. When false, save() returns an unsaved instance of the model.
    #     # When save() calls are made by the Django admin, commit is pretty
    #     # much invariably false, though I'm not sure why. This is a problem
    #     # because when creating a new case instance, it needs to have been
    #     # saved in the DB and have a PK, before we can create CaseSetupScript.
    #     # Fortunately, all models have a built-in method called save_m2m()
    #     # which will always be executed after save(), and we can append our
    #     # CaseSetupScript-creating code to the existing same_m2m() method.
    #     commit = kwargs.get('commit', True)
    #     # Save the case and get an instance of the saved model
    #     instance = super(CaseAdminForm, self).save(*args, **kwargs)
    #     # This is known as a lexical closure, which means that if we store
    #     # this function and execute it later on, it will execute in the same
    #     # context (i.e. it will have access to the current instance and self).
    #     def save_m2m():
    #         # This is really naive code and should be improved upon,
    #         # especially in terms of validation, but the basic gist is to make
    #         # the needed CaseSetupScript. For now, we'll just delete any
    #         # existing CaseSetupScript for this case and create them anew.
    #         CaseSetupScript.objects.filter(case=instance).delete()
    #         # Make a list of (rank, script ID) tuples from the comma-
    #         # -separated list of script IDs we get from the results field.
    #         formdata = enumerate(map(int, self.cleaned_data['results'].split(',')), 1)
    #         for rank, script in formdata:
    #             CaseSetupScript.objects.create(case=instance, script=script, rank=rank)
    #     if commit:
    #         # If we're committing (fat chance), simply run the closure.
    #         save_m2m()
    #     else:
    #         # Using a function concatenator, ensure our save_m2m closure is
    #         # called after the existing save_m2m function (which will be
    #         # called later on if commit is False).
    #         self.save_m2m = func_concat(self.save_m2m, save_m2m)
    #     # Return the instance like a good save() method.
    #     return instance
