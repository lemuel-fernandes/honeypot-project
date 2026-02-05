import os

# -----------------------------
# Auth / Deployment settings
# -----------------------------
# Guvi will ask you for:
# - Header name: x-api-key
# - Honeypot API Endpoint URL: <your-deployed-base-url>/api/honeypot
API_KEY = os.getenv("HONEYPOT_API_KEY", "sk_test_123456789")

# Keep this "0" in production. Helpful for quick local testing.
ALLOW_DEV_KEY = os.getenv("HONEYPOT_ALLOW_DEV_KEY", "0") == "1"

# -----------------------------
# Guvi mandatory callback
# -----------------------------
GUVI_CALLBACK = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

# If you want to disable callbacks during local testing:
CALLBACK_ENABLED = os.getenv("HONEYPOT_CALLBACK_ENABLED", "1") == "1"

# -----------------------------
# Scam detection config
# -----------------------------
SCAM_KEYWORDS = [
    # banking / account
    "bank",
    "account",
    "blocked",
    "freeze",
    "suspend",
    "suspension",
    "debit",
    "credit",
    "kYC",
    "kyc",
    "verify",
    "verification",
    "otp",
    "pin",
    "cvv",
    "password",
    # payments / UPI
    "upi",
    "paytm",
    "phonepe",
    "gpay",
    "google pay",
    "bharatpe",
    "transaction",
    "refund",
    "reversal",
    # urgency / threats
    "urgent",
    "immediately",
    "within",
    "today",
    "last chance",
    # links / phishing
    "link",
    "click",
    "http",
    "www",
]

# After how many total message exchanges we send the final callback (once per session).
FINAL_CALLBACK_MIN_TURNS = int(os.getenv("HONEYPOT_FINAL_CALLBACK_MIN_TURNS", "6"))