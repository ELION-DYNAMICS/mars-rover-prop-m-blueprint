from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk_size)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def read_yaml_simple(path: Path) -> Dict[str, Any]:
    # Keep dependencies minimal: parse a tiny subset of YAML using json when possible.
    # If you want full YAML, add PyYAML explicitly later.
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except Exception:
        # extremely small YAML subset: only handles "topics:\n  - x" style
        data: Dict[str, Any] = {}
        lines = [ln.rstrip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")]
        key = None
        for ln in lines:
            if ln.endswith(":") and not ln.startswith("-"):
                key = ln[:-1].strip()
                data[key] = []
            elif ln.strip().startswith("-") and key is not None:
                data[key].append(ln.split("-", 1)[1].strip())
        return data


def write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")