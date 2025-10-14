import os
import fcntl
from contextlib import contextmanager
from typing import Dict, List

from django import http
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt


PUBLISHED_BASE_DIR = "/home/nordup/projects/thegates-folder/thegates-backend/staticfiles/published"
STATICFILES_DIR = "/home/nordup/projects/thegates-folder/thegates-backend/staticfiles"
LOCAL_BASE_URL = "http://127.0.0.1:8000/"
PUBLIC_BASE_URL = "https://thegates.io/worlds"

# Maximum sizes (in bytes) per extension
_ALLOWED_EXTENSIONS: Dict[str, int] = {
    ".gate": 10 * 1024 * 1024,
    ".png": 30 * 1024 * 1024,
    ".zip": 500 * 1024 * 1024,
}

# Persistent counter storage for publishing user ids
_COUNTER_DIR = os.path.join(PUBLISHED_BASE_DIR, "_meta")
_COUNTER_FILE = os.path.join(_COUNTER_DIR, "user_counter.txt")


def _safe_segment(value: str, fallback: str) -> str:
    # slugify enforces [a-z0-9-]+; fall back if nothing remains
    candidate = slugify(str(value or "").strip())
    if candidate:
        return candidate
    fallback_candidate = slugify(fallback.strip())
    return fallback_candidate or "default"


def _ensure_directory(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _save_uploaded_file(destination: str, uploaded_file) -> None:
    with open(destination, "wb") as dest:
        for chunk in uploaded_file.chunks():
            dest.write(chunk)


def _build_url(base_url: str, relative_path: str) -> str:
    base = base_url.rstrip("/")
    rel = relative_path.lstrip("/")
    return f"{base}/{rel}"


@contextmanager
def _locked_file(path: str):
    _ensure_directory(os.path.dirname(path))
    f = open(path, "a+")  # create if missing
    try:
        f.seek(0)
        fcntl.flock(f, fcntl.LOCK_EX)
        yield f
    finally:
        try:
            f.flush()
            os.fsync(f.fileno())
        except Exception:
            pass
        try:
            fcntl.flock(f, fcntl.LOCK_UN)
        finally:
            f.close()


def _increment_user_count() -> int:
    with _locked_file(_COUNTER_FILE) as f:
        content = f.read().strip()
        try:
            current_value = int(content) if content else 0
        except ValueError:
            current_value = 0
        next_value = current_value + 1
        f.seek(0)
        f.truncate()
        f.write(str(next_value))
        return next_value


@csrf_exempt
def create_publishing_user_id(request: http.HttpRequest) -> http.HttpResponse:
    if request.method != "POST":
        return http.HttpResponse(status=405)

    next_number = _increment_user_count()
    user_id = f"user_{next_number}"
    return http.JsonResponse({
        "status": "ok",
        "code": "created",
        "user_id": user_id,
        "number": next_number,
    }, status=201)


def _is_truthy(value: str | None) -> bool:
    if value is None:
        return False
    return value.lower() in {"1", "true", "yes", "on"}


def _gate_base_url() -> str:
    if _is_truthy(os.getenv("SERVER_LOCAL")):
        return LOCAL_BASE_URL
    return PUBLIC_BASE_URL


def _error_response(code: str, message: str, http_status: int = 400, **extra) -> http.JsonResponse:
    payload = {"status": "error", "code": code, "message": message}
    payload.update(extra)
    return http.JsonResponse(payload, status=http_status)


def _validate_files(files: List) -> http.JsonResponse | None:
    for uploaded in files:
        filename = os.path.basename(uploaded.name or "")
        _, ext = os.path.splitext(filename)
        ext = ext.lower()
        if ext not in _ALLOWED_EXTENSIONS:
            return _error_response(
                "unsupported_file_type",
                "Unsupported file type",
                filename=filename,
                allowed_extensions=sorted(_ALLOWED_EXTENSIONS.keys()),
            )
        max_size = _ALLOWED_EXTENSIONS[ext]
        if uploaded.size is not None and uploaded.size > max_size:
            return _error_response(
                "file_too_large",
                "File exceeds maximum allowed size",
                filename=filename,
                limit_bytes=max_size,
                actual_bytes=uploaded.size,
            )
    return None


@csrf_exempt
def publish_project(request: http.HttpRequest) -> http.HttpResponse:
    if request.method != "POST":
        return http.HttpResponse(status=405)

    user_id = request.POST.get("user_id", "")
    project_name = request.POST.get("project_name", "")
    files = request.FILES.getlist("files") if hasattr(request, "FILES") else []

    if not user_id.strip():
        return _error_response("missing_user_id", "Missing user_id")
    if not project_name.strip():
        return _error_response("missing_project_name", "Missing project_name")
    if not files:
        return _error_response("no_files", "No files uploaded")

    validation_response = _validate_files(files)
    if validation_response:
        return validation_response

    extensions_present = set()
    for uploaded in files:
        _, ext = os.path.splitext(os.path.basename(uploaded.name or ""))
        extensions_present.add(ext.lower())

    missing_exts = []
    for required in (".gate", ".zip"):
        if required not in extensions_present:
            missing_exts.append(required)

    if missing_exts:
        return _error_response(
            "missing_required_extensions",
            "Missing required file types",
            missing_extensions=missing_exts,
        )

    user_dir = _safe_segment(user_id, "user")
    project_dir = _safe_segment(project_name, "project")
    target_dir = os.path.join(PUBLISHED_BASE_DIR, user_dir, project_dir)

    _ensure_directory(target_dir)

    gate_file_url = None
    for uploaded in files:
        filename = os.path.basename(uploaded.name or "")
        destination = os.path.join(target_dir, filename)
        _save_uploaded_file(destination, uploaded)
        if gate_file_url is None and filename.lower().endswith(".gate"):
            relative_path = os.path.relpath(destination, STATICFILES_DIR)
            gate_file_url = _build_url(_gate_base_url(), relative_path)

    return http.JsonResponse(
        {
            "status": "ok",
            "code": "published",
            "url": gate_file_url,
        },
        status=201,
    )


@csrf_exempt
def get_published_project(request: http.HttpRequest) -> http.HttpResponse:
    if request.method != "GET":
        return http.HttpResponse(status=405)

    user_id = request.GET.get("user_id", "")
    project_name = request.GET.get("project_name", "")

    if not user_id.strip():
        return _error_response("missing_user_id", "Missing user_id")
    if not project_name.strip():
        return _error_response("missing_project_name", "Missing project_name")

    user_dir = _safe_segment(user_id, "user")
    project_dir = _safe_segment(project_name, "project")
    project_path = os.path.join(PUBLISHED_BASE_DIR, user_dir, project_dir)

    gate_path = None
    if os.path.isdir(project_path):
        for candidate in os.listdir(project_path):
            if candidate.lower().endswith(".gate"):
                gate_path = os.path.join(project_path, candidate)
                break

    if not gate_path:
        return _error_response(
            "not_found",
            "Published project not found",
            http_status=404,
        )

    relative_path = os.path.relpath(gate_path, STATICFILES_DIR)
    gate_url = _build_url(_gate_base_url(), relative_path)

    return http.JsonResponse(
        {
            "status": "ok",
            "code": "published",
            "url": gate_url,
        }
    )
