from django.shortcuts import render
from django.http import HttpResponse
from .azure_models import *
from os import *
from capstone_project.settings import BASE_DIR
from json import dumps


# Create your views here.

def home(request):
    return HttpResponse(os.path.realpath(__file__))


def dashboard(request):
    # display our interactive graphs
    return render(request, 'dashboard.html')


def test(request):
    data = [-1, -1]

    if request.method == "POST":
        # get file names
        uploaded_image = request.FILES["image"]
        uploaded_csv = request.FILES["file"]

        print(uploaded_image)
        print(uploaded_csv)

        azure_models = AzureModels()
        osteo_data = azure_models.formatOsteosarcomaData(uploaded_csv.name)
        histo_data = azure_models.formatHistopathData(uploaded_image.name)

        responses = azure_models.consumeEndpoints(osteo_data, histo_data)

        data = azure_models.sanitizeResponses(responses)
        data = dumps(data)

    # main page to test the model
    # this is where we will call the function from azure_models.py
    return render(request, 'test.html', {"data": data})