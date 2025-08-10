from __future__ import annotations

from typing import Any, Dict, Optional, Callable, TypeVar, cast
from functools import wraps
from flask import request, jsonify
from google.oauth2 import id_token
from google.auth.transport import requests

from ..config import AppConfig


class FirebaseVerifier:
    def __init__(self, config: AppConfig) -> None:
        self._project_id: Optional[str] = config.firebase_project_id
        self._request = requests.Request()

    @property
    def enabled(self) -> bool:
        return bool(self._project_id)

    def verify(self, token: str) -> Dict[str, Any]:
        if not self.enabled:
            raise ValueError("Firebase verification not configured")
        payload = id_token.verify_firebase_token(token, self._request, audience=self._project_id)
        return payload or {}


F = TypeVar("F", bound=Callable[..., Any])

def firebase_required(func: F) -> F:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        verifier: FirebaseVerifier = getattr(request, "app_ctx_firebase", None)
        if not verifier or not verifier.enabled:
            return jsonify({"error": "Auth not configured"}), 500
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing bearer token"}), 401
        token = auth_header.split(" ", 1)[1]
        try:
            payload = verifier.verify(token)
        except Exception:
            return jsonify({"error": "Invalid token"}), 401
        setattr(request, "firebase_user", {
            "uid": payload.get("user_id"),
            "email": payload.get("email"),
            "name": payload.get("name"),
            "picture": payload.get("picture"),
        })
        return func(*args, **kwargs)
    return cast(F, wrapper)


def get_firebase_email() -> Optional[str]:
    user = getattr(request, "firebase_user", None) or {}
    return cast(Optional[str], user.get("email"))