from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from django.conf import settings


class FlutterwaveGatewayError(Exception):
    """Raised when a Flutterwave request fails or returns an invalid payload."""

    def __init__(self, message: str, status_code: int = 500, payload=None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


@dataclass
class FlutterwaveClient:
    """Minimal Flutterwave API client for checkout initialization and verification."""

    base_url: str = settings.FLUTTERWAVE_BASE_URL.rstrip("/")
    timeout: int = 30

    def _request(self, method: str, path: str, payload=None):
        secret_key = settings.FLUTTERWAVE_SECRET_KEY
        if not secret_key:
            raise FlutterwaveGatewayError(
                "Flutterwave secret key is not configured.",
                status_code=500,
            )

        body = None
        headers = {
            "Authorization": f"Bearer {secret_key}",
            "Accept": "application/json",
        }

        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = urllib.request.Request(
            url=f"{self.base_url}{path}",
            data=body,
            headers=headers,
            method=method,
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw_payload = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raw_payload = exc.read().decode("utf-8")
            try:
                parsed_payload = json.loads(raw_payload) if raw_payload else {}
            except json.JSONDecodeError:
                parsed_payload = raw_payload

            message = (
                parsed_payload.get("message")
                if isinstance(parsed_payload, dict)
                else raw_payload or "Flutterwave request failed."
            )
            raise FlutterwaveGatewayError(
                str(message),
                status_code=exc.code,
                payload=parsed_payload,
            ) from exc
        except urllib.error.URLError as exc:
            raise FlutterwaveGatewayError(
                f"Unable to reach Flutterwave: {exc.reason}",
                status_code=502,
            ) from exc

        try:
            parsed_payload = json.loads(raw_payload) if raw_payload else {}
        except json.JSONDecodeError as exc:
            raise FlutterwaveGatewayError(
                "Flutterwave returned an invalid JSON payload.",
                status_code=502,
                payload=raw_payload,
            ) from exc

        if parsed_payload.get("status") != "success":
            raise FlutterwaveGatewayError(
                parsed_payload.get("message", "Flutterwave request failed."),
                status_code=502,
                payload=parsed_payload,
            )

        return parsed_payload

    def initialize_payment(self, payload):
        return self._request("POST", "/payments", payload)

    def verify_transaction(self, transaction_id):
        return self._request("GET", f"/transactions/{transaction_id}/verify")
