from __future__ import annotations

from typing import Any, Dict, List
from flask import Blueprint, jsonify, request
from firebase_admin import firestore as fa_firestore

from ..db import Database
from ..services.gemini_client import GeminiClient
from ..utils.firebase_auth import firebase_required


chat_bp = Blueprint("chat_bp", __name__, url_prefix="/api/chat")


def _get_uid() -> str | None:
  fb_user = getattr(request, "firebase_user", None) or {}
  return fb_user.get("uid")


@chat_bp.post("")
@firebase_required
def chat():
    db: Database = request.app_ctx_db  # type: ignore[attr-defined]
    gemini: GeminiClient = request.app_ctx_gemini  # type: ignore[attr-defined]

    user_uid = _get_uid()
    if not user_uid:
        return jsonify({"error": "Unauthorized"}), 401

    payload: Dict[str, Any] = request.get_json(silent=True) or {}
    question: str = payload.get("message", "")

    user_doc_ref = db.users.document(user_uid)
    query = user_doc_ref.collection("pathways").order_by(
        "createdAt", direction=fa_firestore.Query.DESCENDING
    ).limit(1)
    docs = list(query.stream())
    context = {"plan": (docs[0].to_dict() or {}).get("plan")} if docs else None

    messages: List[Dict[str, str]] = [{"role": "user", "content": question}]
    answer = gemini.chat(messages, context=context)

    db.chats.add({
        "userId": user_uid,
        "message": question,
        "answer": answer,
        "createdAt": fa_firestore.SERVER_TIMESTAMP,
    })

    return jsonify({"answer": answer}), 200