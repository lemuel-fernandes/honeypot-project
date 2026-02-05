from __future__ import annotations

from typing import Any, Dict

# In-memory session store (good enough for hackathon eval).
# For production you’d swap this with Redis/Postgres.
sessions: Dict[str, Dict[str, Any]] = {}