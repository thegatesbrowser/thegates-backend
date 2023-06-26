from django.views.decorators.csrf import csrf_exempt
from django import http
import requests
import json


def save_gate(url: str) -> str:
    print("Save gate: " + url)
    pass


@csrf_exempt
def discover_gate(req: http.HttpRequest) -> http.HttpResponse:
    data = json.loads(req.body)
    print(data)
    
    return http.HttpResponse(status=200)
