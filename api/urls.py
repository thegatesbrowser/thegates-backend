from django.urls import path, re_path
from . import analytics
from . import search
from . import gate


urlpatterns = [
    path('api/analytics_event', analytics.analytics_event),
    path('api/get_user_id', analytics.get_user_id),
    path('api/discover_gate', gate.discover_gate),
    path('api/search', search.search)
]
