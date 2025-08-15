from django.urls import path, re_path
from . import views
from . import downloads

urlpatterns = [
    path('downloads/<str:platform>-latest', downloads.latest),
    re_path('.*', views.every),
    path('', views.every),
]
