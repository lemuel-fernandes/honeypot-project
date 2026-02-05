from __future__ import annotations

import re
from typing import Iterable, Tuple

from app.config import SCAM_KEYWORDS


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def detect_scam(text: str) -> Tuple[bool, list[str]]:
    """
    Heuristic scam intent detector.
    Returns: (is_scam, matched_keywords)
    """
    t = _normalize(text)
    if not t:
        return False, []

    matched = [k for k in SCAM_KEYWORDS if k.lower() in t]

    # Strong patterns (even if keyword list misses)
    strong_patterns = [
        r"\bupi\b",
        r"\botp\b",
        r"\bkyc\b",
        r"https?://\S+",
        r"\b\d{10}\b",  # 10-digit phone
        r"\b\d{6}\b",  # OTP-like
        r"\b(?:account|a/c)\b.*\b(?:blocked|freeze|suspend)\b",
    ]
    strong_hit = any(re.search(p, t) for p in strong_patterns)

    # Decision rule: any strong hit OR enough weak keyword hits
    is_scam = strong_hit or (len(matched) >= 2)
    return is_scam, matched