from django.views.decorators.csrf import csrf_exempt
from django import http


@csrf_exempt
def analytics_event(req: http.HttpRequest) -> http.HttpResponse:
    print(req.body)
    return http.HttpResponse(status=200)

@csrf_exempt
def get_user_id(req: http.HttpRequest) -> http.HttpResponse:
    if req.method == 'GET':
        device_id = req.GET.get('device_id', '')
        if device_id != '': return http.HttpResponse(content=device_id) # TODO: combine with IP address
    return http.HttpResponse(status=400)