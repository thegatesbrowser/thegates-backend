import os
import secrets
import shutil
import uuid
from typing import Dict, List

from django import http
from django.conf import settings
from django.db import IntegrityError, transaction
from django.views.decorators.csrf import csrf_exempt

from myapp.models import PublishingProject


# Resolve storage paths from Django settings instead of hard-coded absolute paths
STATICFILES_DIR = getattr(settings, "STATIC_ROOT", os.path.join(settings.BASE_DIR, "staticfiles"))
PUBLISHED_BASE_DIR = os.path.join(STATICFILES_DIR, "published")

LOCAL_BASE_URL = "http://127.0.0.1:8000/"
PUBLIC_BASE_URL = "https://thegates.io/worlds"

# Maximum sizes (in bytes) per extension
_ALLOWED_EXTENSIONS: Dict[str, int] = {
    ".gate": 10 * 1024 * 1024,
    ".png": 30 * 1024 * 1024,
    ".zip": 500 * 1024 * 1024,
}


def _generate_project_id() -> str:
    return uuid.uuid4().hex


def _generate_token() -> str:
    # token_urlsafe(32) produces ~43 char tokens, well within the model limit
    return secrets.token_urlsafe(32)


def _ensure_directory(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _reset_directory(path: str) -> None:
    if os.path.isdir(path):
        shutil.rmtree(path)
    _ensure_directory(path)


def _save_uploaded_file(destination: str, uploaded_file) -> None:
    with open(destination, "wb") as dest:
        for chunk in uploaded_file.chunks():
            dest.write(chunk)


def _build_url(base_url: str, relative_path: str) -> str:
    base = base_url.rstrip("/")
    rel = relative_path.lstrip("/")
    return f"{base}/{rel}"


def _is_truthy(value: str | None) -> bool:
    if value is None:
        return False
    return value.lower() in {"1", "true", "yes", "on"}


def _gate_base_url() -> str:
    if _is_truthy(os.getenv("SERVER_LOCAL")):
        return LOCAL_BASE_URL
    return PUBLIC_BASE_URL


def _build_project_url(project_id: str, filename: str) -> str:
    return _build_url(_gate_base_url(), f"{project_id}/{filename}")


def _error_response(code: str, message: str, http_status: int = 400, **extra) -> http.JsonResponse:
    payload = {"status": "error", "code": code, "message": message}
    payload.update(extra)
    return http.JsonResponse(payload, status=http_status)


def _alloc_project() -> PublishingProject:
    # Attempt a few times to avoid rare collisions
    for _ in range(5):
        token = _generate_token()
        project_id = _generate_project_id()
        try:
            with transaction.atomic():
                return PublishingProject.objects.create(token=token, project_id=project_id)
        except IntegrityError:
            continue
    raise RuntimeError("unable_to_allocate_project")


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
def create_project(request: http.HttpRequest) -> http.HttpResponse:
    if request.method != "POST":
        return http.HttpResponse(status=405)

    try:
        project = _alloc_project()
    except RuntimeError:
        return _error_response(
            "allocation_failed",
            "Unable to allocate project. Please retry.",
            http_status=500,
        )

    return http.JsonResponse(
        {
            "status": "ok",
            "code": "created",
            "project_id": project.project_id,
            "token": project.token,
        },
        status=201,
    )


@csrf_exempt
def publish_project(request: http.HttpRequest) -> http.HttpResponse:
    if request.method != "POST":
        return http.HttpResponse(status=405)

    token = request.POST.get("token", "").strip()
    files = request.FILES.getlist("files") if hasattr(request, "FILES") else []

    if not token:
        return _error_response("missing_token", "Missing project token")
    if not files:
        return _error_response("no_files", "No files uploaded")

    try:
        project = PublishingProject.objects.get(token=token)
    except PublishingProject.DoesNotExist:
        return _error_response("invalid_token", "Unknown project token", http_status=404)

    validation_response = _validate_files(files)
    if validation_response:
        return validation_response

    extensions_present = {os.path.splitext(os.path.basename(uploaded.name or ""))[1].lower() for uploaded in files}

    missing_exts = [ext for ext in (".gate", ".zip") if ext not in extensions_present]
    if missing_exts:
        return _error_response(
            "missing_required_extensions",
            "Missing required file types",
            missing_extensions=missing_exts,
        )

    target_dir = os.path.join(PUBLISHED_BASE_DIR, project.project_id)
    _reset_directory(target_dir)

    gate_filename = None
    for uploaded in files:
        filename = os.path.basename(uploaded.name or "")
        destination = os.path.join(target_dir, filename)
        _save_uploaded_file(destination, uploaded)
        if filename.lower().endswith(".gate"):
            gate_filename = filename

    if gate_filename is None:
        return _error_response(
            "missing_gate_file",
            "Published content must include a .gate file",
        )

    gate_url = _build_project_url(project.project_id, gate_filename)
    project.published_url = gate_url
    project.save(update_fields=["published_url", "updated_at"])
    return http.JsonResponse(
        {
            "status": "ok",
            "code": "published",
            "project_id": project.project_id,
            "url": gate_url,
        },
        status=201,
    )


@csrf_exempt
def get_published_project(request: http.HttpRequest) -> http.HttpResponse:
    if request.method != "GET":
        return http.HttpResponse(status=405)

    token = request.GET.get("token", "").strip()

    if not token:
        return _error_response("missing_token", "Missing project token")

    try:
        project = PublishingProject.objects.get(token=token)
    except PublishingProject.DoesNotExist:
        return _error_response("not_found", "Project not found", http_status=404)

    if not project.published_url:
        return _error_response("not_found", "Published project not found", http_status=404)

    return http.JsonResponse(
        {
            "status": "ok",
            "code": "published",
            "url": project.published_url,
            "project_id": project.project_id,
        }
    )
