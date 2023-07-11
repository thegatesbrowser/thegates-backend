from django.urls import path, re_path
from . import analytics
from . import search
from . import gate


urlpatterns = [
    path('api/analytics_event', analytics.analytics_event),
    path('api/create_user_id', analytics.create_user_id),
    path('api/get_user_id', analytics.get_user_id), # DEPRECATED from TheGates 0.5.2
    path('api/discover_gate', gate.discover_gate),
    path('api/search', search.search)
]
