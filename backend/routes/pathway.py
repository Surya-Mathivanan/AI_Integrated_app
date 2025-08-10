from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from flask import Blueprint, jsonify, request
from firebase_admin import firestore as fa_firestore

from ..db import Database
from ..services.gemini_client import GeminiClient
from ..utils.firebase_auth import firebase_required, get_firebase_email
from ..content_catalog import get_curated_sections, build_daily_resources


pathway_bp = Blueprint("pathway_bp", __name__, url_prefix="/api/pathway")


def _get_uid() -> Optional[str]:
    fb_user = getattr(request, "firebase_user", None) or {}
    return fb_user.get("uid")


def _merge_completion(plan: Dict[str, Any], completed_ids: Set[str]) -> Dict[str, Any]:
    plan = dict(plan)
    sections = plan.get("sections") or {}
    for key in ("codingProblems", "youtubeReferences", "theoryContent"):
        items = list((sections.get(key) or []))
        for it in items:
            if isinstance(it, dict) and it.get("id") in completed_ids:
                it["completed"] = True
        sections[key] = items
    plan["sections"] = sections
    return plan


@pathway_bp.post("/generate")
@firebase_required
def generate_pathway():
    db: Database = request.app_ctx_db  # type: ignore[attr-defined]
    gemini: GeminiClient = request.app_ctx_gemini  # type: ignore[attr-defined]

    questionnaire: Dict[str, Any] = request.get_json(silent=True) or {}
    user_uid = _get_uid()
    user_email = get_firebase_email()
    if not user_uid:
        return jsonify({"error": "Unauthorized"}), 401

    # Ensure user document exists (doc id = uid)
    user_doc_ref = db.users.document(user_uid)
    user_doc_ref.set(
        {
            "email": user_email,
            "name": getattr(request, "firebase_user", {}).get("name", "User"),
            "profileComplete": True,
            "updatedAt": fa_firestore.SERVER_TIMESTAMP,
            "createdAt": fa_firestore.SERVER_TIMESTAMP,
        },
        merge=True,
    )

    # Generate schedule/title via LLM
    plan_llm = gemini.generate_pathway(questionnaire)

    # Enrich each day with day-specific resources
    language = str(questionnaire.get("programmingLanguage", "python"))
    daily = list((plan_llm.get("schedule") or {}).get("daily", []))
    enriched_daily: List[Dict[str, Any]] = []
    for day in daily:
        topics = day.get("topics") or []
        links = build_daily_resources(language, topics if isinstance(topics, list) else [])
        new_day = dict(day)
        new_day["resources"] = links
        enriched_daily.append(new_day)

    # Replace sections with curated content based on combination
    curated = get_curated_sections(questionnaire)
    plan = {
        "title": plan_llm.get("title") or "DSA Pathway",
        "schedule": {"daily": enriched_daily},
        "sections": curated,
    }

    record = {
        "questionnaire": questionnaire,
        "plan": plan,
        "progress": {"completedItemIds": []},
        "createdAt": fa_firestore.SERVER_TIMESTAMP,
        "updatedAt": fa_firestore.SERVER_TIMESTAMP,
    }
    # Write into per-user subcollection
    user_doc_ref.collection("pathways").add(record)
    # Store snapshot
    user_doc_ref.set({"currentPathway": plan, "updatedAt": fa_firestore.SERVER_TIMESTAMP}, merge=True)
    return jsonify({"pathway": plan}), 201


@pathway_bp.post("/new")
@firebase_required
def new_pathway_session():
    db: Database = request.app_ctx_db  # type: ignore[attr-defined]
    user_uid = _get_uid()
    if not user_uid:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        user_ref = db.users.document(user_uid)
        # Ensure the user doc exists
        user_ref.set({"updatedAt": fa_firestore.SERVER_TIMESTAMP}, merge=True)
        # Remove snapshot field if present (ignore if missing)
        try:
            user_ref.update({
                "currentPathway": fa_firestore.DELETE_FIELD,
                "updatedAt": fa_firestore.SERVER_TIMESTAMP,
            })
        except Exception:
            pass
        return jsonify({"ok": True}), 200
    except Exception:
        # Do not block the wizard if reset fails
        return jsonify({"ok": True}), 200


@pathway_bp.get("/current")
@firebase_required
def get_current_pathway():
    db: Database = request.app_ctx_db  # type: ignore[attr-defined]
    user_uid = _get_uid()
    if not user_uid:
        return jsonify({"pathway": None}), 200

    user_doc_ref = db.users.document(user_uid)
    # Read most recent from subcollection to get progress
    query = user_doc_ref.collection("pathways").order_by(
        "createdAt", direction=fa_firestore.Query.DESCENDING
    ).limit(1)
    docs = list(query.stream())
    snapshot_plan: Dict[str, Any] | None = None
    if docs:
        doc_data = docs[0].to_dict() or {}
        progress = (doc_data.get("progress") or {})
        completed_ids = set(progress.get("completedItemIds", []))
        plan = doc_data.get("plan") or {}
        merged = _merge_completion(plan, completed_ids)
        snapshot_plan = merged

    if snapshot_plan is not None:
        return jsonify({"pathway": snapshot_plan}), 200

    # Fallback to snapshot field
    snap = user_doc_ref.get()
    if snap.exists:
        data = snap.to_dict() or {}
        if data.get("currentPathway"):
            return jsonify({"pathway": data.get("currentPathway")}), 200

    return jsonify({"pathway": None}), 200


@pathway_bp.patch("/progress")
@firebase_required
def update_progress():
    db: Database = request.app_ctx_db  # type: ignore[attr-defined]
    user_uid = _get_uid()
    if not user_uid:
        return jsonify({"error": "Unauthorized"}), 401

    payload: Dict[str, Any] = request.get_json(silent=True) or {}
    item_id = payload.get("itemId")
    if not item_id or not isinstance(item_id, str):
        return jsonify({"error": "Missing itemId"}), 400

    user_doc_ref = db.users.document(user_uid)
    query = user_doc_ref.collection("pathways").order_by(
        "createdAt", direction=fa_firestore.Query.DESCENDING
    ).limit(1)
    docs = list(query.stream())
    if not docs:
        return jsonify({"error": "No pathway"}), 404

    doc = docs[0]
    data = doc.to_dict() or {}
    progress = (data.get("progress") or {})
    completed: List[str] = list(progress.get("completedItemIds", []))
    if item_id not in completed:
        completed.append(item_id)

    doc.reference.update(
        {
            "progress.completedItemIds": completed,
            "updatedAt": fa_firestore.SERVER_TIMESTAMP,
        }
    )
    return jsonify({"ok": True, "completedItemIds": completed}), 200


@pathway_bp.post("/adjust")
@firebase_required
def adjust_pathway():
    db: Database = request.app_ctx_db  # type: ignore[attr-defined]
    gemini: GeminiClient = request.app_ctx_gemini  # type: ignore[attr-defined]
    user_uid = _get_uid()
    if not user_uid:
        return jsonify({"error": "Unauthorized"}), 401

    payload: Dict[str, Any] = request.get_json(silent=True) or {}

    user_doc_ref = db.users.document(user_uid)
    query = user_doc_ref.collection("pathways").order_by(
        "createdAt", direction=fa_firestore.Query.DESCENDING
    ).limit(1)
    docs = list(query.stream())
    if not docs:
        return jsonify({"error": "No pathway"}), 404

    data = docs[0].to_dict() or {}
    context = {"plan": data.get("plan"), "progress": data.get("progress")}
    message = {
        "role": "user",
        "content": payload.get("note", "Please adjust my plan based on my progress."),
    }
    suggestion = gemini.chat([message], context=context)
    return jsonify({"adjustment": suggestion}), 200


@pathway_bp.get("/list")
@firebase_required
def list_pathways():
    db: Database = request.app_ctx_db  # type: ignore[attr-defined]
    user_uid = _get_uid()
    if not user_uid:
        return jsonify({"items": [], "total": 0}), 200
    user_doc_ref = db.users.document(user_uid)
    query = user_doc_ref.collection("pathways").order_by(
        "createdAt", direction=fa_firestore.Query.DESCENDING
    )
    items: List[Dict[str, Any]] = []
    for doc in query.stream():
        data = doc.to_dict() or {}
        title = (data.get("plan") or {}).get("title", "Untitled Pathway")
        days = len(((data.get("plan") or {}).get("schedule") or {}).get("daily", []))
        created_at = data.get("createdAt")
        created_iso = None
        try:
            created_iso = created_at.to_datetime().isoformat() if created_at else None
        except Exception:
            created_iso = None
        items.append({
            "id": doc.id,
            "title": title,
            "days": days,
            "createdAt": created_iso,
        })
    return jsonify({"items": items, "total": len(items)}), 200