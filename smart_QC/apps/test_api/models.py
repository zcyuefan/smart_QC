from __future__ import unicode_literals

from django.db import models

# Create your models here.
REQUEST_METHODS = (
    ('GET', 'GET'),
    ('POST', 'POST'),
    ('DELETE', 'DELETE'),
    ('PUT', 'PUT'),
)


class OriginalAPI(models.Model):
    #
    module = models.CharField(max_length=20)
    tags = models.CharField(max_length=20)
    # request
    method = models.CharField(max_length=10, choices=REQUEST_METHODS)
    protocol = models.CharField(max_length=10)
    host = models.CharField(max_length=30)
    api = models.CharField(max_length=30)
    query_string = models.TextField()
    post_data = models.TextField()
    request_headers = models.TextField()
    request_cookies = models.TextField()
    # response
    response_status = models.DecimalField()
    response_headers = models.TextField()
    response_cookies = models.TextField()
    response_content = models.TextField()
    # api run timings
    timings_total = models.DecimalField()
    timings_blocked = models.DecimalField()
    timings_dns = models.DecimalField()
    timings_connect = models.DecimalField()
    timings_send = models.DecimalField()
    timings_wait = models.DecimalField()
    timings_receive = models.DecimalField()
    timings_ssl = models.DecimalField()
    #
    create_time = models.DateTimeField(auto_now=True)
    modify_time = models.DateTimeField(auto_now=True)