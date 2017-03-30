from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def index(request):
    return HttpResponse('Hello world')


def home(request):
    return render(request, 'website/home.html')

from smart_QC.apps.test_api.tasks import add
add.delay(2, 2)