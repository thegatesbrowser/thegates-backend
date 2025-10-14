import os
import json
import uuid
import re
from api.integrations import mixpanel
from api.integrations import notifications
from django import http
from django.db.models import Q
from myapp.models import Users
from ua_parser import user_agent_parser
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction, IntegrityError


def _extract_os_from_user_agent(req: http.HttpRequest) -> str:
    # Try to extract OS from "GodotEngine/4.3.1.rc.custom_build (Platform)"
    user_agent = req.headers.get("User-Agent", "")
    match = re.search(r'\(([^)]+)\)', user_agent or "")
    if match:
        candidate = match.group(1).strip()
        if candidate:
            return candidate
    
    # Fallback to parsed os family
    parsed = user_agent_parser.Parse(user_agent or "")
    return (parsed.get("os", {}) or {}).get("family")


def _generate_unique_user_id() -> str:
	while True:
		user_id = str(uuid.uuid4())
		user_id_query = Q(user_id__icontains=user_id)
		if not Users.objects.filter(user_id_query).exists():
			return user_id


@csrf_exempt
def analytics_event(req: http.HttpRequest) -> http.HttpResponse:
    if os.getenv('SERVER_LOCAL'): return http.HttpResponse(status=200)
    
    data = json.loads(req.body)
    data['ip'] = req.META['HTTP_X_REAL_IP']
    data["$os"] = _extract_os_from_user_agent(req)
    
    if data.get('user_id') == 'none':
        print('Error: Event with \'none\' user_id')
        return http.HttpResponse(status=400)
    
    mixpanel.track(data.copy())
    notifications.notify_application_open(data.copy())
    return http.HttpResponse(status=200)


@csrf_exempt
def create_user_id(req: http.HttpRequest) -> http.HttpResponse:
    if req.method != 'GET':
        return http.HttpResponse(status=400)
    
    device_id = req.GET.get('device_id')

    if not device_id:
        user_id = _generate_unique_user_id()
        user = Users(user_id=user_id, device_id=None)
        user.save()

        print('generated new user_id ' + user_id)
        return http.HttpResponse(content=user_id)

    # Race-safe creation: try get_or_create in an atomic block; if a concurrent
    # request creates the same device_id, catch IntegrityError and fetch.
    was_created = False
    try:
        with transaction.atomic():
            user, created = Users.objects.get_or_create(
                device_id=device_id,
                defaults={"user_id": _generate_unique_user_id()},
            )
            was_created = created
    except IntegrityError:
        user = Users.objects.get(device_id=device_id)

    print('created new' if was_created else 'got existing', 'user_id ' + user.user_id + ' for device_id ' + device_id)
    return http.HttpResponse(content=user.user_id)
