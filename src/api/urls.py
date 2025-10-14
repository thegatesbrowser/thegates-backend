from django.urls import path
from . import analytics
from . import search
from . import gate
from . import logs
from . import uploads
from . import renderer_downloads
from . import publishing


urlpatterns = [
    path('api/analytics_event', analytics.analytics_event),
    path('api/create_user_id', analytics.create_user_id),
    path('api/discover_gate', gate.discover_gate),
    path('api/featured_gates', gate.featured_gates),
    path('api/all_gates', gate.all_gates),
    path('api/search', search.search),
    path('api/prompt', search.prompt),
    path('api/send_logs', logs.send_logs),
    path('api/upload_build', uploads.upload_build),
    path('api/publish_project', publishing.publish_project),
    path('api/get_published_project', publishing.get_published_project),
    path('api/create_publishing_user_id', publishing.create_publishing_user_id),
    path('api/download_renderer/<str:platform>-<str:version>', renderer_downloads.download_renderer),
]
