from django.shortcuts import render
from django.http import HttpResponse
from .azure_models import *
from os import *
from capstone_project.settings import BASE_DIR
from json import dumps
import pandas as pd
from io import StringIO

# Create your views here.

def home(request):
    return HttpResponse(os.path.realpath(__file__))


def dashboard(request):
    # display our interactive graphs
    return render(request, 'dashboard.html')


def test(request):
    if request.method == "POST":
        # get file contents
        uploaded_image = request.FILES["image"]
        uploaded_csv = request.FILES["file"]

        models = AzureModels()
        data = models.combinedModel(uploaded_csv, uploaded_image)
        if(data == 'no_tumor'):
            data = "Sample indicates non-cancerous"
        else:
            data = "Sample indicates cancerous"

        return render(request, 'test.html', {"result": data})

    # main page to test the model
    # this is where we will call the function from azure_models.py
    return render(request, 'test.html')