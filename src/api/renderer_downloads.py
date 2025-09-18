import os
from django import http
from django.views.decorators.csrf import csrf_exempt


RENDERERS_DIR = "/home/thegates/projects/the-gates-backend/staticfiles/builds/renderers"


@csrf_exempt
def download_renderer(request: http.HttpRequest, platform: str, version: str) -> http.HttpResponse:
    if request.method != "GET":
        return http.HttpResponse(status=405)

    filename = f"{platform}-{version}.zip"
    file_path = os.path.join(RENDERERS_DIR, filename)

    if not os.path.isfile(file_path):
        return http.HttpResponse(status=404)

    response = http.HttpResponse()
    response["Content-Type"] = "application/zip"
    response["Content-Disposition"] = f"attachment; filename=\"{filename}\""
    response["X-Accel-Redirect"] = f"/protected_downloads/renderers/{filename}"
    return response


