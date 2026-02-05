from __future__ import annotations

import re
from typing import Dict, List


def extract_intel(text: str) -> Dict[str, List[str]]:
    """
    Extract scam intelligence from the latest message text.
    Returns lists; caller can merge into session store.
    """
    t = text or ""

    # UPI IDs (common formats: name@bank, phone@upi)
    upi_ids = re.findall(r"\b[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}\b", t)

    # Phone numbers: +91XXXXXXXXXX or 10-digit
    phone_numbers = re.findall(r"(?:\+91[-\s]?)?\b\d{10}\b", t)

    # Links
    phishing_links = re.findall(r"https?://\S+|www\.\S+", t)

    # Bank account-like sequences (very loose; we keep it conservative)
    bank_accounts = re.findall(r"\b\d{9,18}\b", t)

    def _dedupe(xs: List[str]) -> List[str]:
        seen = set()
        out: List[str] = []
        for x in xs:
            x2 = x.strip()
            if not x2 or x2 in seen:
                continue
            seen.add(x2)
            out.append(x2)
        return out

    return {
        "bankAccounts": _dedupe(bank_accounts),
        "upiIds": _dedupe(upi_ids),
        "phishingLinks": _dedupe(phishing_links),
        "phoneNumbers": _dedupe(phone_numbers),
    }