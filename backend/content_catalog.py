from __future__ import annotations

from typing import Any, Dict, List, Tuple
from urllib.parse import quote_plus


def _assign_ids(items: List[Dict[str, Any]], prefix: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for i, it in enumerate(items, start=1):
        x = dict(it)
        x.setdefault("id", f"{prefix}-{i}")
        out.append(x)
    return out

# Curated content catalog keyed by (level, hoursBucket, language)
# Add more combinations as needed.
_CATALOG: Dict[Tuple[str, str, str], Dict[str, List[Dict[str, Any]]]] = {
    ("beginner", "1-2", "python"): {
        "codingProblems": [
            {"title": "Arrays: Basics (LeetCode easy)"},
            {"title": "Strings: Intro problems"},
            {"title": "HashMap: Frequency counting"},
            {"title": "Two Pointers: Simple pairs"},
        ],
        "youtubeReferences": [
            {"title": "Python DSA Crash Course", "url": "https://www.youtube.com/results?search_query=python+dsa+crash+course"},
            {"title": "Arrays in Python", "url": "https://www.youtube.com/results?search_query=python+arrays+tutorial"},
        ],
        "theoryContent": [
            {"title": "Big-O Notation (CP-Algorithms)", "url": "https://cp-algorithms.com/"},
            {"title": "Python Official Docs", "url": "https://docs.python.org/3/"},
        ],
    },
    ("intermediate", "2-3", "java"): {
        "codingProblems": [
            {"title": "Linked List: Reverse & Cycle"},
            {"title": "Stack/Queue: Next Greater Element"},
            {"title": "Binary Search: Peak Element"},
        ],
        "youtubeReferences": [
            {"title": "Java DSA Playlist", "url": "https://www.youtube.com/results?search_query=java+dsa+playlist"},
        ],
        "theoryContent": [
            {"title": "Java Collections Guide", "url": "https://docs.oracle.com/javase/tutorial/collections/"},
        ],
    },
}

# Fallbacks: level+language, then level only, then generic defaults per language
_FALLBACK_LEVEL_LANG: Dict[Tuple[str, str], Dict[str, List[Dict[str, Any]]]] = {
    ("beginner", "python"): {
        "codingProblems": [{"title": "Arrays & Strings practice set"}],
        "youtubeReferences": [{"title": "Python DSA Beginner", "url": "https://www.youtube.com"}],
        "theoryContent": [{"title": "Basics of Complexity", "url": "https://cp-algorithms.com"}],
    }
}

_FALLBACK_LEVEL: Dict[str, Dict[str, List[Dict[str, Any]]]] = {
    "beginner": {
        "codingProblems": [{"title": "Intro DSA problems"}],
        "youtubeReferences": [{"title": "DSA Intro", "url": "https://www.youtube.com"}],
        "theoryContent": [{"title": "Asymptotic Notation", "url": "https://cp-algorithms.com"}],
    },
    "intermediate": {
        "codingProblems": [{"title": "Mid-level DSA problems"}],
        "youtubeReferences": [{"title": "Intermediate DSA"}],
        "theoryContent": [{"title": "Data Structures Deep Dive"}],
    },
    "advanced": {
        "codingProblems": [{"title": "Advanced DSA problems"}],
        "youtubeReferences": [{"title": "Advanced Topics"}],
        "theoryContent": [{"title": "Advanced Algorithms"}],
    },
}

_GENERIC_LANG: Dict[str, Dict[str, List[Dict[str, Any]]]] = {
    "python": {
        "codingProblems": [{"title": "LeetCode Python Warmups"}],
        "youtubeReferences": [{"title": "Python DSA", "url": "https://www.youtube.com"}],
        "theoryContent": [{"title": "Python Docs", "url": "https://docs.python.org/3/"}],
    },
    "java": {
        "codingProblems": [{"title": "LeetCode Java Warmups"}],
        "youtubeReferences": [{"title": "Java DSA", "url": "https://www.youtube.com"}],
        "theoryContent": [{"title": "Oracle Docs", "url": "https://docs.oracle.com/javase/"}],
    },
}

_DEFAULT: Dict[str, List[Dict[str, Any]]] = {
    "codingProblems": [{"title": "Starter Problems"}],
    "youtubeReferences": [{"title": "DSA Playlist", "url": "https://www.youtube.com"}],
    "theoryContent": [{"title": "Big-O Reference", "url": "https://cp-algorithms.com"}],
}


def get_curated_sections(questionnaire: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    level = str(questionnaire.get("skillLevel", "beginner")).lower()
    hours = str(questionnaire.get("hoursPerDay", "1-2"))
    language = str(questionnaire.get("programmingLanguage", "python")).lower()

    for key in [
        (level, hours, language),
    ]:
        if key in _CATALOG:
            c = _CATALOG[key]
            return {
                "codingProblems": _assign_ids(c.get("codingProblems", []), "cp"),
                "youtubeReferences": _assign_ids(c.get("youtubeReferences", []), "yt"),
                "theoryContent": _assign_ids(c.get("theoryContent", []), "th"),
            }

    if (level, language) in _FALLBACK_LEVEL_LANG:
        c = _FALLBACK_LEVEL_LANG[(level, language)]
        return {
            "codingProblems": _assign_ids(c.get("codingProblems", []), "cp"),
            "youtubeReferences": _assign_ids(c.get("youtubeReferences", []), "yt"),
            "theoryContent": _assign_ids(c.get("theoryContent", []), "th"),
        }

    if level in _FALLBACK_LEVEL:
        c = _FALLBACK_LEVEL[level]
        return {
            "codingProblems": _assign_ids(c.get("codingProblems", []), "cp"),
            "youtubeReferences": _assign_ids(c.get("youtubeReferences", []), "yt"),
            "theoryContent": _assign_ids(c.get("theoryContent", []), "th"),
        }

    if language in _GENERIC_LANG:
        c = _GENERIC_LANG[language]
        return {
            "codingProblems": _assign_ids(c.get("codingProblems", []), "cp"),
            "youtubeReferences": _assign_ids(c.get("youtubeReferences", []), "yt"),
            "theoryContent": _assign_ids(c.get("theoryContent", []), "th"),
        }

    return {
        "codingProblems": _assign_ids(_DEFAULT.get("codingProblems", []), "cp"),
        "youtubeReferences": _assign_ids(_DEFAULT.get("youtubeReferences", []), "yt"),
        "theoryContent": _assign_ids(_DEFAULT.get("theoryContent", []), "th"),
    }


def build_daily_resources(language: str, topics: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    """Build day-specific links based on topics. Uses search URLs for LC/GFG/YT."""
    items_problems: List[Dict[str, Any]] = []
    items_youtube: List[Dict[str, Any]] = []
    items_theory: List[Dict[str, Any]] = []

    for t in topics[:3]:
        q = quote_plus(t)
        q_lang = quote_plus(f"{language} {t} DSA")
        items_problems.append({
            "title": f"{t} - LeetCode search",
            "url": f"https://leetcode.com/problemset/?search={q}",
        })
        items_problems.append({
            "title": f"{t} - GfG search",
            "url": f"https://www.geeksforgeeks.org/?s={q}",
        })
        items_youtube.append({
            "title": f"{t} - YouTube",
            "url": f"https://www.youtube.com/results?search_query={q_lang}",
        })
        items_theory.append({
            "title": f"{t} - GfG topics",
            "url": f"https://www.geeksforgeeks.org/?s={q}",
        })

    return {
        "practice": _assign_ids(items_problems, "dpr"),
        "youtube": _assign_ids(items_youtube, "dyt"),
        "theory": _assign_ids(items_theory, "dth"),
    }