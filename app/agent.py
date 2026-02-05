from __future__ import annotations

import random
from typing import Dict, List


def agent_reply(
    *,
    latest_text: str,
    turn: int,
    matched_keywords: List[str],
    extracted_intel: Dict[str, List[str]],
    channel: str | None = None,
) -> str:
    """
    A lightweight "agentic" response generator (no external LLM).
    Goal: keep the scammer engaged and elicit intel.
    """
    channel = (channel or "").strip() or "SMS"
    t = (latest_text or "").lower()

    # If we already got a link / UPI / phone, ask follow-ups that increase intel quality.
    if extracted_intel.get("phishingLinks"):
        return "That link isn't opening for me. Can you send the exact full link again and tell me what I'm supposed to do after opening it?"
    if extracted_intel.get("upiIds"):
        return "I'm not sure my UPI app is showing the right screen. Which app should I use (GPay/PhonePe/Paytm) and what exactly should I enter?"
    if extracted_intel.get("phoneNumbers"):
        return "I'm getting calls from different numbers. Which number should I call back or reply to so this gets fixed quickly?"
    if "otp" in t or "pin" in t or "password" in t or "cvv" in t:
        return "I received something but I'm confused - what is this code for, and why did it come now? Can you explain what step I'm on?"

    # Early turns: act worried/confused; ask for “official” details.
    if turn <= 2:
        return random.choice(
            [
                "What do you mean my account will be blocked? Which bank are you from and what exactly happened?",
                "I'm outside right now. Can you tell me the last 4 digits or any reference number so I can confirm it's really my account?",
                "I didn't do any transaction today - what is the issue exactly? Please explain step by step.",
            ]
        )

    # Mid turns: ask for procedural details that reveal scam workflow.
    if turn <= 5:
        return random.choice(
            [
                "Okay, what should I do first - should I click any link or open my UPI app? Tell me the exact steps.",
                "You said it's urgent. What happens if I don't do it now, and what proof do you have that this is official?",
                "Can you send the official message format again? I want to show it to my family and be sure I'm doing it correctly.",
            ]
        )

    # Later turns: keep stalling while extracting more.
    kw = ", ".join(sorted(set(matched_keywords))[:4])
    if kw:
        return f"I'm trying to follow. You mentioned {kw} - can you confirm the exact process and the contact/UPI details one more time so I don't make a mistake?"

    return "I'm still confused. Can you explain the steps again and share the exact contact details so I can complete it?"