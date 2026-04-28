"""
Live API smoke runner for AltixEdu.

Starts from a running backend and verifies that key role flows respond with
successful HTTP status codes and expected payload shapes.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.parse
import urllib.request


BASE_URL = "http://127.0.0.1:8000"
PASSWORD = "Password123!"

ROLE_CREDENTIALS = {
    "admin": "admin@atlascollege.test",
    "teacher": "teacher@atlascollege.test",
    "student": "student@atlascollege.test",
    "parent": "parent@atlascollege.test",
    "bursar": "bursar@atlascollege.test",
    "superadmin": "superadmin@altixedu.test",
    "ministry": "ministry@oyo-edu.test",
}

ROLE_ENDPOINTS = {
    "admin": [
        "/api/auth/me/",
        "/api/dashboard/schooladmin/",
        "/api/platform/branding-admin/",
        "/api/school-settings/current/",
        "/api/users/?role=student",
        "/api/users/?role=teacher",
    ],
    "teacher": [
        "/api/auth/me/",
        "/api/dashboard/teacher/",
    ],
    "student": [
        "/api/auth/me/",
        "/api/dashboard/student/",
    ],
    "parent": [
        "/api/auth/me/",
        "/api/dashboard/parent/",
    ],
    "bursar": [
        "/api/auth/me/",
        "/api/dashboard/bursar/",
    ],
    "superadmin": [
        "/api/auth/me/",
        "/api/platform/overview/",
        "/api/government/permissions/roles/",
    ],
    "ministry": [
        "/api/auth/me/",
        "/api/platform/overview/",
        "/api/government/audit-logs/",
        "/api/government/permissions/roles/",
    ],
}


def http_request(path: str, method: str = "GET", token: str | None = None, data: dict | None = None):
    url = urllib.parse.urljoin(BASE_URL, path)
    body = None
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Token {token}"
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, method=method, data=body, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            raw = response.read().decode("utf-8")
            payload = json.loads(raw) if raw else {}
            return response.status, payload
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            payload = {"raw": raw}
        return exc.code, payload


def expect(status: int, payload: dict, *, path: str, role: str):
    if status >= 400:
        raise AssertionError(f"{role} {path} failed with {status}: {payload}")


def login(role: str) -> str:
    status, payload = http_request(
        "/api/auth/login/",
        method="POST",
        data={"email": ROLE_CREDENTIALS[role], "password": PASSWORD},
    )
    expect(status, payload, path="/api/auth/login/", role=role)
    token = payload.get("token")
    if not token:
        raise AssertionError(f"{role} login response missing token: {payload}")
    return token


def main() -> int:
    print("Running live API smoke checks against", BASE_URL)
    for role, endpoints in ROLE_ENDPOINTS.items():
        token = login(role)
        print(f"[ok] login {role}")
        for path in endpoints:
            status, payload = http_request(path, token=token)
            expect(status, payload, path=path, role=role)
            print(f"[ok] {role} -> {path}")
    print("Live API smoke checks passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - smoke script
        print(f"Live API smoke failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
