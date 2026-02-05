from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

import requests
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.agent import agent_reply
from app.config import (
    ALLOW_DEV_KEY,
    API_KEY,
    CALLBACK_ENABLED,
    FINAL_CALLBACK_MIN_TURNS,
    GUVI_CALLBACK,
    SCAM_KEYWORDS,
)
from app.detector import detect_scam
from app.extractor import extract_intel
from app.storage import sessions

Sender = Literal["scammer", "user"]


class Message(BaseModel):
    sender: Sender
    text: str
    timestamp: int


class Metadata(BaseModel):
    channel: Optional[str] = None
    language: Optional[str] = None
    locale: Optional[str] = None


class HoneypotRequest(BaseModel):
    sessionId: str = Field(..., min_length=1)
    message: Message
    conversationHistory: List[Message] = Field(default_factory=list)
    metadata: Optional[Metadata] = None


app = FastAPI(title="Agentic HoneyPot API", version="1.0.0")


def verify_key(x_api_key: str = Header(..., alias="x-api-key")) -> None:
    if API_KEY == "sk_test_123456789" and ALLOW_DEV_KEY:
        return
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key or malformed request")


@app.exception_handler(HTTPException)
def _http_exception_handler(_, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"status": "error", "message": str(exc.detail)})


@app.exception_handler(RequestValidationError)
def _validation_exception_handler(_, __: RequestValidationError):
    return JSONResponse(status_code=400, content={"status": "error", "message": "Invalid API key or malformed request"})


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


def _init_session() -> Dict[str, Any]:
    return {
        "count": 0,
        "scamDetected": False,
        "callbackSent": False,
        "intel": {"bankAccounts": [], "upiIds": [], "phishingLinks": [], "phoneNumbers": []},
        "matchedKeywords": [],
        "agentNotes": "",
    }


def _merge_intel(session: Dict[str, Any], intel: Dict[str, List[str]]) -> None:
    for k, vals in intel.items():
        if k not in session["intel"]:
            session["intel"][k] = []
        for v in vals:
            if v not in session["intel"][k]:
                session["intel"][k].append(v)


def _send_final_callback(session_id: str, session: Dict[str, Any]) -> None:
    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": int(session.get("count", 0)),
        "extractedIntelligence": {
            "bankAccounts": session["intel"].get("bankAccounts", []),
            "upiIds": session["intel"].get("upiIds", []),
            "phishingLinks": session["intel"].get("phishingLinks", []),
            "phoneNumbers": session["intel"].get("phoneNumbers", []),
            "suspiciousKeywords": sorted(set(session.get("matchedKeywords", []))),
        },
        "agentNotes": session.get("agentNotes") or "Scam conversation engaged and intel extracted.",
    }
    try:
        requests.post(GUVI_CALLBACK, json=payload, timeout=5)
    except Exception:
        # Callback failures shouldn't break the API response during evaluation
        pass


@app.post("/api/honeypot")
def honeypot(req: HoneypotRequest, key: None = Depends(verify_key)) -> Dict[str, Any]:
    sid = req.sessionId
    latest_text = req.message.text
    channel = req.metadata.channel if req.metadata else None

    if sid not in sessions:
        sessions[sid] = _init_session()

    s = sessions[sid]
    s["count"] += 1

    # Detect scam intent from latest message (and optionally from history)
    is_scam, matched = detect_scam(latest_text)
    if matched:
        s["matchedKeywords"] = sorted(set(s.get("matchedKeywords", []) + matched))

    # Keep scamDetected sticky once true
    if is_scam:
        s["scamDetected"] = True

    if not s["scamDetected"]:
        return {"status": "success", "reply": "Okay."}

    # Extract intel from latest message
    intel = extract_intel(latest_text)
    _merge_intel(s, intel)

    # Generate agent response (human-like, non-revealing)
    s["agentNotes"] = "Engaged scammer without revealing detection."
    reply = agent_reply(
        latest_text=latest_text,
        turn=int(s["count"]),
        matched_keywords=s.get("matchedKeywords", []),
        extracted_intel=s.get("intel", {}),
        channel=channel,
    )

    # Mandatory final callback (once)
    if (
        CALLBACK_ENABLED
        and s["scamDetected"]
        and not s.get("callbackSent", False)
        and int(s["count"]) >= FINAL_CALLBACK_MIN_TURNS
    ):
        _send_final_callback(sid, s)
        s["callbackSent"] = True

    return {"status": "success", "reply": reply}