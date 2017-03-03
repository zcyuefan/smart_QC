#!/usr/bin/env python
# encoding=utf-8

# Author zhangchao@jinwantai.com
# date:2017/2/28
# topic: 
# update: 

"""
model模块公共方法库
"""
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _


def AbstractClassWithoutFieldsNamed(cls, *excl):
    """
    Removes unwanted fields from abstract base classes.
    Usage::
    # >>> from oscar.apps.address.abstract_models import AbstractBillingAddress
    # >>> from koe.meta import AbstractClassWithoutFieldsNamed as without
    # >>> class BillingAddress(without(AbstractBillingAddress, 'phone_number')):
    # ...     pass
    """
    if cls._meta.abstract:
        from copy import deepcopy
        tmp = deepcopy(cls)
        remove_fields = [f for f in tmp._meta.local_fields if f.name in excl]
        for f in remove_fields:
            tmp._meta.local_fields.remove(f)
        return tmp
    else:
        raise Exception("Not an abstract model")


class BaseModel(models.Model):
    name = models.CharField(max_length=40, unique=True)
    description = models.TextField(max_length=255, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    modify_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
