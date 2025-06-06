from django.urls import path
from . import analytics
from . import search
from . import gate
from . import logs


urlpatterns = [
    path('api/analytics_event', analytics.analytics_event),
    path('api/create_user_id', analytics.create_user_id),
    path('api/discover_gate', gate.discover_gate),
    path('api/featured_gates', gate.featured_gates),
    path('api/all_gates', gate.all_gates),
    path('api/search', search.search),
    path('api/prompt', search.prompt),
    path('api/search_suggestions', search.search_suggestions),
    path('api/send_logs', logs.send_logs),
]
