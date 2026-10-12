"""Save and load results as JSON files so we don't pay for the same AI call twice."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Type

from pydantic import BaseModel


def load_cached(path: Path, schema: Type[BaseModel]) -> dict | None:
    """Return validated cached data as a dict, or None if missing/invalid."""
    if not path.exists():
        return None
    try:
        return schema.model_validate_json(path.read_text(encoding="utf-8")).model_dump()
    except (ValueError, OSError):
        return None


def save_cached(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
