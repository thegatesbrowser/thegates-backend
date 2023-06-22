from django.views.decorators.csrf import csrf_exempt
from ua_parser import user_agent_parser
from django import http
from . import mixpanel
import json


@csrf_exempt
def analytics_event(req: http.HttpRequest) -> http.HttpResponse:
    parsed = user_agent_parser.Parse(req.headers["User-Agent"])
    data = json.loads(req.body)

    data["$os"]        = parsed["os"]["family"]
    data['ip']         = req.META['REMOTE_ADDR']

    mixpanel.track(data)
    return http.HttpResponse(status=200)


@csrf_exempt
def get_user_id(req: http.HttpRequest) -> http.HttpResponse:
    if req.method == 'GET':
        device_id = req.GET.get('device_id', '')
        if device_id != '': return http.HttpResponse(content=device_id) # TODO: combine with IP address
    return http.HttpResponse(status=400)
