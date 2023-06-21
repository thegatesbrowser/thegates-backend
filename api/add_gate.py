from django.views.decorators.csrf import csrf_exempt
from django import http
import requests
import json


def save_gate(url: str) -> str:
    print("Save gate: " + url)
    pass


@csrf_exempt
def add_gate(req: http.HttpRequest) -> http.HttpResponse:
    if req.method == 'POST':
        url = req.GET.get('url', '')
        url = requests.utils.unquote(url)
        if url != '':
            save_gate(url)
            return http.HttpResponse(status=200)
    
    return http.HttpResponse(status=400)
