# Agentic Honey-Pot (Problem Statement 2)

Public REST API for scam detection + agentic engagement + intelligence extraction, protected with `x-api-key`.

## Endpoint

- `POST /api/honeypot`
- **Headers**
  - `Content-Type: application/json`
  - `x-api-key: <YOUR_SECRET_API_KEY>`

## Request (Guvi format)

```json
{
  "sessionId": "wertyu-dfghj-ertyui",
  "message": {
    "sender": "scammer",
    "text": "Your bank account will be blocked today. Verify immediately.",
    "timestamp": 1770005528731
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

## Response

```json
{
  "status": "success",
  "reply": "Why is my account being suspended?"
}
```

## Mandatory final callback (Guvi)

When scam intent is confirmed and enough turns have passed, the API sends a final summary to:
`https://hackathon.guvi.in/api/updateHoneyPotFinalResult`

## Environment variables (deployment)

- `HONEYPOT_API_KEY` (**required**): the API key Guvi will send as `x-api-key`
- `HONEYPOT_ALLOW_DEV_KEY` (default `0`): set `1` only for local testing
- `HONEYPOT_CALLBACK_ENABLED` (default `1`): set `0` to disable callback during local testing
- `HONEYPOT_FINAL_CALLBACK_MIN_TURNS` (default `6`): turns required before sending callback once

## Run locally

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```