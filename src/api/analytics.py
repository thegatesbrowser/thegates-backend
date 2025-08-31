import os
import json
import uuid
from api.integrations import mixpanel
from api.integrations import telegram
from django import http
from django.db.models import Q
from myapp.models import Users
from ua_parser import user_agent_parser
from django.views.decorators.csrf import csrf_exempt


def _generate_unique_user_id() -> str:
	while True:
		user_id = str(uuid.uuid4())
		user_id_query = Q(user_id__icontains=user_id)
		if not Users.objects.filter(user_id_query).exists():
			return user_id


@csrf_exempt
def analytics_event(req: http.HttpRequest) -> http.HttpResponse:
    if os.getenv('DISABLE_ANALYTICS'): return http.HttpResponse(status=200)
    
    parsed = user_agent_parser.Parse(req.headers["User-Agent"])
    
    data = json.loads(req.body)
    data["$os"] = parsed["os"]["family"]
    data['ip'] = req.META['HTTP_X_REAL_IP']
    
    mixpanel.track(data.copy())
    telegram.bot_notify_event(data.copy())
    return http.HttpResponse(status=200)


@csrf_exempt
def create_user_id(req: http.HttpRequest) -> http.HttpResponse:
    if req.method != 'GET':
        return http.HttpResponse(status=400)
    
    device_id = req.GET.get('device_id')
    user = Users.objects.filter(device_id=device_id).first() if device_id else None
    if user is not None:
        return http.HttpResponse(content=user.user_id)
    
    user_id = _generate_unique_user_id()
    print('generated new user_id ' + user_id)
    
    user = Users(user_id=user_id, device_id=device_id)
    user.save()
    
    return http.HttpResponse(content=user_id)
