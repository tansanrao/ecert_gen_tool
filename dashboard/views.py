from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from .models import CsvFile
from django.conf import settings
import json
import os
import pandas as pd
import requests

# JSReport API config
jsreport_api_endpoint = "http://localhost:5488/api/report"
jsreport_headers = {
    "Content-Type": "application/json"
}


def index(request):
    context = {}
    template = loader.get_template('dashboard/home.html')
    return HttpResponse(template.render(context, request))


def gentella_html(request):
    context = {}
    load_template = request.path.split('/')[-1]
    if request.method == 'POST' and request.FILES['file']:
        myfile = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        print(uploaded_file_url)

        csv_instance = CsvFile.objects.create(filename=myfile.name, filepath=uploaded_file_url)

        template = loader.get_template('dashboard/' + load_template)
        context['uploaded_file_url'] = uploaded_file_url
        context['uploaded_file_id'] = csv_instance.id
        return HttpResponse(json.dumps(context))
    # The template to be loaded as per gentelella.
    # All resource paths for gentelella end in .html.

    # Pick out the html file name from the url. And load that template.
    template = loader.get_template('dashboard/' + load_template)
    return HttpResponse(template.render(context, request))


def generateCerts(request):
    context = {}
    if request.method == 'POST':
        reqdata = json.loads(request.body)
        print(reqdata)
        certgen_data = pd.read_csv(os.path.join(settings.BASE_DIR + reqdata['uploaded_file_url']))
        json_data = json.loads(certgen_data.to_json(orient="records"))

        if reqdata['certgen_cert_type'] == 'email':
            for record in json_data:
                recArray = []
                recArray.append(record)
                payload = {
                    "template": {"shortid": "rJxeRw5xjS"},
                    "data": {"records": recArray}
                }
                print(payload)
                jsreport_response = requests.post(jsreport_api_endpoint, json=payload, headers=jsreport_headers)
                with open('/tmp/'+record['name']+'.pdf', 'wb') as fd:
                    fd.write(jsreport_response.content)

        else:
            payload = {
                "template": {"shortid": "rJxeRw5xjS"},
                "data": {"records": json_data}
            }
            print(payload)
            jsreport_response = requests.post(jsreport_api_endpoint, json=payload, headers=jsreport_headers)
            with open('/tmp/certprint.pdf', 'wb') as fd:
                fd.write(jsreport_response.content)
            return HttpResponse("/tmp/certprint.pdf ")
