#!/usr/bin/env python
# encoding=utf-8
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.utils.translation import ugettext as _


# # Create your views here.
# def index(request):
#     return HttpResponse(_("hello"))
#
#
# def home(request):
#     return render(request, 'website/home.html')
#     # return HttpResponse(settings_for_env.MEDIA_ROOT)
#
#
# def guojihua(request):
#     # return render(request, 'website/home.html')
#     code = _("The second sentence is from the Python code.")
#     response_context = {'lang': request.LANGUAGE_CODE,
#                         'code': code
#                         }
#     resp = render(request, 'website/guojihua_test.html', response_context)
#     # resp = render_to_response('website/guojihua_test.html', responseContext)
#     return resp