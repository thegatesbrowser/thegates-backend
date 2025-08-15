import os
import re
from django import http
from django.views.decorators.csrf import csrf_exempt


BUILDS_DIR = "/home/thegates/projects/the-gates-backend/staticfiles/builds"


def _parse_version(version_str):
    parts = version_str.split(".")
    try:
        return tuple(int(p) for p in parts)
    except ValueError:
        return tuple()


def _find_latest_filename(platform_key):
    platform_map = {
        "linux": "TheGates_Linux_",
        "windows": "TheGates_Windows_",
        "mac": "TheGates_MacOS_",
        "macos": "TheGates_MacOS_",
        "osx": "TheGates_MacOS_",
    }

    prefix = platform_map.get(platform_key.lower())
    if prefix is None:
        return None

    if not os.path.isdir(BUILDS_DIR):
        return None

    candidates = []
    for fname in os.listdir(BUILDS_DIR):
        if not fname.startswith(prefix) or not fname.endswith(".zip"):
            continue
        m = re.match(re.escape(prefix) + r"([0-9][0-9\.]+)\.zip$", fname)
        if not m:
            continue
        ver = _parse_version(m.group(1))
        candidates.append((ver, fname))

    if not candidates:
        return None

    candidates.sort()
    return candidates[-1][1]


@csrf_exempt
def latest(request, platform):
    if request.method != "GET":
        return http.HttpResponse(status=405)

    latest_filename = _find_latest_filename(platform)
    if latest_filename is None:
        return http.HttpResponse(status=404)

    response = http.HttpResponse()
    response["Content-Type"] = "application/zip"
    response["Content-Disposition"] = f"attachment; filename=\"{latest_filename}\""
    response["X-Accel-Redirect"] = f"/protected_downloads/{latest_filename}"
    return response


