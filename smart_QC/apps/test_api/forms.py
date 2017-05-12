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
from .models import Case


class CaseForm(forms.ModelForm):
    class Meta:
        model = Case
        exclude = []

    def clean(self):
        print(self.cleaned_data)
