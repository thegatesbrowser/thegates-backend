from django.urls import path, re_path
from . import views
from . import search


urlpatterns = [
    path('api/analytics_event', views.analytics_event),
    path('api/get_user_id', views.get_user_id),
    path('api/search', search.search)
]
