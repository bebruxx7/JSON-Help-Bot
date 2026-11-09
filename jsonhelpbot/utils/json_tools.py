from __future__ import annotations

import json
from typing import Any

MAX_JSON_TEXT = 3500


def dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, default=str)


def loads_payload(raw: str | None) -> dict[str, Any] | None:
    if not raw:
        return None
    stripped = raw.strip()
    if not stripped.startswith("{"):
        return None
    try:
        data = json.loads(stripped)
    except json.JSONDecodeError:
        return None
    if isinstance(data, dict) and isinstance(data.get("type"), str):
        return data
    return None
