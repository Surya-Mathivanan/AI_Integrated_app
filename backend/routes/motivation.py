from __future__ import annotations

from typing import List
from flask import Blueprint, jsonify
from cachetools import TTLCache

motivation_bp = Blueprint("motivation_bp", __name__, url_prefix="/api/motivation")

_cache = TTLCache(maxsize=1, ttl=60 * 30)  # 30 minutes

_DEFAULT_TIPS: List[str] = [
    "Small progress every day adds up to big results.",
    "Consistency beats intensity.",
    "Focus on one key concept at a time.",
    "Practice is the best teacher.",
]


@motivation_bp.get("")
def get_tips():
    tips = _cache.get("tips")
    if tips is None:
        tips = _DEFAULT_TIPS
        _cache["tips"] = tips
    return jsonify({"tips": tips}), 200