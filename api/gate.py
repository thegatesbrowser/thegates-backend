from django.views.decorators.csrf import csrf_exempt
from django import http
import requests
import json
from myapp.models import Gates


def is_local(url: str) -> bool:
    return "://localhost" in url \
        or "://127.0.0.1" in url \
        or "://0.0.0.0" in url


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

    if is_local(url):
        return http.HttpResponse(status=200)
    
    gates = Gates.objects.filter(url=url)
    if gates.count() < 1:
        gate = Gates(url=url, title=title, description=description, image=image, resource_pack=resource_pack) #, libraries=libraries
        gate.save()
        print("Discovered gate: " + url)
    else:
        gate = gates[0]
        gate.url = url
        gate.title = title
        gate.description = description
        gate.image = image
        gate.resource_pack = resource_pack
    
    return http.HttpResponse(status=200)
