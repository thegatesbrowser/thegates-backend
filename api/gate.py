from django.views.decorators.csrf import csrf_exempt
from django import http
import requests
import json
from myapp.models import Gates


def save_gate(url: str) -> str:
    print("Save gate: " + url)
    pass


@csrf_exempt
def discover_gate(req: http.HttpRequest) -> http.HttpResponse:
    data = json.loads(req.body)
    print(data)

    url = data['url']
    title = data['title']
    description = data['description']
    image = data['image']
    resource_pack = data['resource_pack']
    # libraries = data['libraries']

    gate = Gates(url=url, title=title, description=description, image=image, resource_pack=resource_pack) #, libraries=libraries
    gate.save()
    
    return http.HttpResponse(status=200)
