from django.shortcuts import render
from django.http import HttpResponse
from .azure_models import *
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
    default_data = pd.read_csv('./capstone_app/static/img/tabulardata.csv')
    data_html = default_data.to_html()
    if request.method == "POST":
        # get file contents
        uploaded_image = request.FILES["image"]
        uploaded_csv = request.FILES["file"]

        models = AzureModels()
        data_test = models.combinedModel(uploaded_csv, uploaded_image)
        if(data_test == 'no_tumor'):
            data_test = "Sample indicates non-cancerous"
        else:
            data_test = "Sample indicates cancerous"
        return render(request, 'test.html', {"result_test": data_test, "loaded_data": data_html})

    else:
        tabular_file = open('./capstone_app/static/img/tabulardata.csv','rb')
        image_file = open('./capstone_app/static/img/demo_image.png','rb')

        models = AzureModels()
        data = models.combinedModel(tabular_file, image_file)
        if (data == 'no_tumor'):
            data = "Sample indicates non-cancerous"
        else:
            data = "Sample indicates cancerous"
        return render(request, 'test.html', {"loaded_data": data_html, "result": data})
    # main page to test the model
    # this is where we will call the function from azure_models.py
    return render(request, 'test.html', {"loaded_data": data_html})