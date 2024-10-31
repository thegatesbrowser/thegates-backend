import os
import requests
import datetime
from django.views.decorators.csrf import csrf_exempt
from django import http
from django.utils import timezone

logs_folder = 'staticfiles/logs'


def create_path(url: str) -> str:
    folder = url.replace('http://', '').replace('https://', '').replace('.gate', '')
    folder = folder.replace(':', '_') # remove ':' before port

    # '%Y-%m-%d_%H-%M-%S'
    # '%Y_%m_%d__%H_%M_%S'
    date = timezone.datetime.now(datetime.UTC)
    path = logs_folder + '/' + folder + '/log__' + date.strftime('%Y_%m_%d__%H_%M_%S') + '.txt'

    return path


@csrf_exempt
def send_logs(req: http.HttpRequest) -> http.HttpResponse:
    if req.method != 'POST': return http.HttpResponse(status=400)

    url = req.GET.get('url', '')
    url = requests.utils.unquote(url)
    
    path = create_path(url)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    file = open(path, 'w')
    file.write(req.body.decode("utf-8"))
    file.close()

    print("Logs saved to " + path)
    return http.HttpResponse(status=200)
