from django.views.decorators.csrf import csrf_exempt
from ua_parser import user_agent_parser
from django import http
from django.db.models import Q
import json
import uuid
from . import mixpanel
from myapp.models import Users


@csrf_exempt
def analytics_event(req: http.HttpRequest) -> http.HttpResponse:
    parsed = user_agent_parser.Parse(req.headers["User-Agent"])
    
    data = json.loads(req.body)
    data["$os"] = parsed["os"]["family"]
    data['ip'] = req.META['REMOTE_ADDR']
    
    mixpanel.track(data)
    return http.HttpResponse(status=200)


@csrf_exempt
def create_user_id(req: http.HttpRequest) -> http.HttpResponse:
    if req.method != 'GET':
        return http.HttpResponse(status=400)
    
    while True:
        user_id = str(uuid.uuid4())
        user_id_query = Q(user_id__icontains = user_id)
        existing_ids = Users.objects.filter(user_id_query)
        if existing_ids.count() == 0: break
    
    print('generated new user_id ' + user_id)
    user = Users(user_id=user_id)
    user.save()
    
    return http.HttpResponse(content=user_id)
