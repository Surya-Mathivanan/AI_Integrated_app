from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from ..config import AppConfig

try:
    import google.generativeai as genai  # type: ignore
except Exception:  # pragma: no cover
    genai = None  # type: ignore


def _parse_days(questionnaire: Dict[str, Any]) -> int:
    prep = str(questionnaire.get("prepTime", "")).lower().strip()
    if not prep and questionnaire.get("days"):
        try:
            return int(questionnaire["days"])
        except Exception:
            pass
    if "day" in prep:
        try:
            return int(prep.split()[0])
        except Exception:
            return 7
    if "week" in prep:
        try:
            return int(prep.split()[0]) * 7
        except Exception:
            return 7
    if "month" in prep:
        try:
            n = int(prep.split()[0])
        except Exception:
            n = 1
        return 30 * n
    return 7


def _ensure_ids(items: List[Dict[str, Any]], prefix: str) -> List[Dict[str, Any]]:
    result: List[Dict[str, Any]] = []
    for idx, it in enumerate(items, start=1):
        it = dict(it)
        if not it.get("id"):
            it["id"] = f"{prefix}-{idx}"
        result.append(it)
    return result


class GeminiClient:
    def __init__(self, config: AppConfig) -> None:
        self._api_key: Optional[str] = config.gemini_api_key
        self._model_name: str = config.model_name
        self.enabled: bool = bool(self._api_key and genai is not None)
        if self.enabled and genai is not None:
            genai.configure(api_key=self._api_key)
            self._model = genai.GenerativeModel(self._model_name)
        else:
            self._model = None
        self._pathway_cache: dict[Tuple[str, str, str, str], Dict[str, Any]] = {}

    def _stub_pathway(self, questionnaire: Dict[str, Any]) -> Dict[str, Any]:
        skill = questionnaire.get("skillLevel", "beginner").title()
        duration = questionnaire.get("prepTime", "1 week")
        language = questionnaire.get("programmingLanguage", "python").title()
        days = _parse_days(questionnaire)
        daily: List[Dict[str, Any]] = []
        day_topics = [
            ["Syntax, Variables, Data Types", "I/O, Conditionals"],
            ["Arrays/Lists", "Common operations", "Two pointers"],
            ["Strings", "Sliding window basics"],
            ["HashMap/Dictionary", "Set"],
            ["Stack & Queue", "Problems"],
            ["Linked List", "Fast/slow pointers"],
            ["Math & Bit Manipulation"],
        ]
        for d in range(1, days + 1):
            topics = day_topics[(d - 1) % len(day_topics)]
            daily.append({
                "day": d,
                "focus": f"{language} & DSA Study Day {d}",
                "time": questionnaire.get("hoursPerDay", "2h"),
                "topics": topics,
                "details": f"Study: {', '.join(topics)}. Practice 3-5 problems based on time.",
            })
        hours_str = str(questionnaire.get("hoursPerDay", "2"))
        coding_cnt = 20
        if hours_str.startswith("2"): coding_cnt = 25
        if hours_str.startswith("3"): coding_cnt = 35
        if hours_str.startswith(">"): coding_cnt = 50
        return {
            "title": f"{skill} DSA Plan ({duration})",
            "schedule": {"daily": daily},
            "sections": {
                "codingProblems": _ensure_ids([
                    {"title": f"{language} Array Basics - Set {i}"} for i in range(1, min(coding_cnt, 60) + 1)
                ], "cp"),
                "youtubeReferences": _ensure_ids([
                    {"title": f"{language} DSA Playlist Part {i}", "url": "https://www.youtube.com"} for i in range(1, 6)
                ], "yt"),
                "theoryContent": _ensure_ids([
                    {"title": f"Big-O Notation Guide {i}", "url": "https://cp-algorithms.com"} for i in range(1, 6)
                ], "th"),
            },
        }

    def generate_pathway(self, questionnaire: Dict[str, Any]) -> Dict[str, Any]:
        if not self.enabled or self._model is None:
            return self._stub_pathway(questionnaire)

        key: Tuple[str, str, str, str] = (
            str(questionnaire.get("skillLevel", "")),
            str(questionnaire.get("prepTime", "")),
            str(questionnaire.get("hoursPerDay", "")),
            str(questionnaire.get("programmingLanguage", "")),
        )
        cached = self._pathway_cache.get(key)
        if cached:
            return cached

        days = _parse_days(questionnaire)
        language = questionnaire.get("programmingLanguage", "python")
        hours = questionnaire.get("hoursPerDay", "2h")
        prompt = (
            "You are an AI mentor. Create a structured DSA plan. STRICT OUTPUT IN JSON ONLY. "
            "Requirements:\n"
            f"- schedule.daily must have EXACTLY {days} items (day 1..{days}).\n"
            "- Each daily item MUST include: day (number), focus (string), time (string), details (2-4 sentences of what to study and practice), topics (array of 3-5 concrete topics).\n"
            "- sections: include codingProblems[], youtubeReferences[], theoryContent[].\n"
            "- Each item in those arrays MUST have a stable string id (e.g., 'cp-1', 'yt-1', 'th-1') and a human-readable title; include url where relevant.\n"
            "- Adjust number of codingProblems based on hoursPerDay (1-2h: ~20, 2-3h: 20-30, 3-4h: 30-40, >4h: 40-60).\n"
            "Context:\n"
            f"skillLevel: {questionnaire.get('skillLevel')}\n"
            f"hoursPerDay: {hours}\n"
            f"programmingLanguage: {language}\n"
            f"prepTime: {questionnaire.get('prepTime')}\n"
            "Return JSON with keys: title, schedule: { daily: [...] }, sections: { codingProblems: [...], youtubeReferences: [...], theoryContent: [...] }."
        )
        response = self._model.generate_content(prompt)
        text = getattr(response, "text", None) or "{}"
        cleaned = text.strip().strip("` ")
        import json
        try:
            data = json.loads(cleaned)
        except Exception:
            data = self._stub_pathway(questionnaire)

        # Post-process: enforce days count and required fields
        try:
            daily = data.get("schedule", {}).get("daily", [])
            if not isinstance(daily, list):
                daily = []
            current: List[Dict[str, Any]] = []
            for idx in range(1, days + 1):
                entry: Dict[str, Any] = {"day": idx, "focus": f"Study Day {idx}", "time": hours, "details": "", "topics": []}
                if idx - 1 < len(daily):
                    src = daily[idx - 1] or {}
                    entry.update({k: src.get(k, entry[k]) for k in ["focus", "time", "details", "topics"]})
                if not isinstance(entry.get("topics"), list):
                    entry["topics"] = []
                current.append(entry)
            data.setdefault("schedule", {})["daily"] = current

            sections = data.get("sections", {}) or {}
            sections["codingProblems"] = _ensure_ids(list(sections.get("codingProblems", [])), "cp")
            sections["youtubeReferences"] = _ensure_ids(list(sections.get("youtubeReferences", [])), "yt")
            sections["theoryContent"] = _ensure_ids(list(sections.get("theoryContent", [])), "th")
            data["sections"] = sections
        except Exception:
            data = self._stub_pathway(questionnaire)

        self._pathway_cache[key] = data
        return data

    def chat(self, messages: List[Dict[str, str]], context: Optional[Dict[str, Any]] = None) -> str:
        if not self.enabled or self._model is None:
            last = messages[-1]["content"] if messages else ""
            return f"[Stub Response]\n\n{last}\n\n- Focus on fundamentals.\n- Practice daily.\n- Review mistakes."

        parts: List[str] = []
        if context:
            parts.append(f"Context: {context}")
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            parts.append(f"{role.upper()}: {content}")
        response = self._model.generate_content("\n".join(parts))
        return getattr(response, "text", "")