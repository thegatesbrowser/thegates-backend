import os
from django import http
from django.views.decorators.csrf import csrf_exempt


BUILDS_DIR = "/home/thegates/projects/the-gates-backend/staticfiles/builds"
API_KEY_FILE = "keys/upload_api.key"
API_KEY_ENV = "UPLOAD_API_KEY"


def _get_api_key():
    key = os.getenv(API_KEY_ENV)
    if key:
        return key.strip()
    if os.path.isfile(API_KEY_FILE):
        try:
            with open(API_KEY_FILE, "r") as f:
                return f.read().strip()
        except Exception:
            return None
    return None


def _extract_provided_key(request: http.HttpRequest):
    # Prefer X-API-Key; also accept Authorization: Bearer <key>
    api_key = request.headers.get("X-API-Key") or request.headers.get("X-Api-Key")
    if api_key:
        return api_key.strip()
    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return None


@csrf_exempt
def upload_build(request: http.HttpRequest) -> http.HttpResponse:
    if request.method != "POST":
        return http.HttpResponse(status=405)

    expected_key = _get_api_key()
    provided_key = _extract_provided_key(request)
    if not expected_key or not provided_key or provided_key != expected_key:
        return http.HttpResponse(status=401)

    # Accept multipart form-data (preferred): field name "file"
    uploaded_file = None
    if hasattr(request, "FILES") and "file" in request.FILES:
        uploaded_file = request.FILES["file"]
        filename = os.path.basename(uploaded_file.name)
        os.makedirs(BUILDS_DIR, exist_ok=True)
        dest_path = os.path.join(BUILDS_DIR, filename)
        with open(dest_path, "wb") as dest:
            for chunk in uploaded_file.chunks():
                dest.write(chunk)
        return http.JsonResponse({
            "status": "ok",
            "filename": filename,
            "path": dest_path,
            "size": uploaded_file.size,
        }, status=201)

    # Fallback: raw body with X-Filename header
    raw_body = request.body
    filename = os.path.basename(request.headers.get("X-Filename", ""))
    if raw_body and filename:
        os.makedirs(BUILDS_DIR, exist_ok=True)
        dest_path = os.path.join(BUILDS_DIR, filename)
        with open(dest_path, "wb") as dest:
            dest.write(raw_body)
        return http.JsonResponse({
            "status": "ok",
            "filename": filename,
            "path": dest_path,
            "size": len(raw_body),
        }, status=201)

    return http.JsonResponse({"error": "No file provided"}, status=400)


