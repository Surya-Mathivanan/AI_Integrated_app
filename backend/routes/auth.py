from __future__ import annotations

from flask import Blueprint, jsonify

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/api/auth")


@auth_bp.get("/info")
def info():
    return jsonify({"auth": "firebase-only"}), 200