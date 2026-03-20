"""Custom errorMessage enrichment from schema."""

from typing import Any


def enrich_message(schema: Any, schema_path: list, keyword: str, default_msg: str) -> str:
    segments = [str(s) for s in schema_path]
    for depth in range(3):
        if depth > len(segments):
            break
        check = segments[:len(segments) - depth] if depth > 0 else segments
        node = _walk(schema, check)
        if isinstance(node, dict) and "errorMessage" in node:
            em = node["errorMessage"]
            if isinstance(em, str):
                return em
            if isinstance(em, dict) and keyword in em:
                return em[keyword]
    return default_msg


def _walk(schema: Any, segments: list[str]) -> Any:
    current = schema
    for seg in segments:
        if isinstance(current, dict):
            current = current.get(seg)
            if current is None:
                return None
        elif isinstance(current, list):
            try:
                current = current[int(seg)]
            except (ValueError, IndexError):
                return None
        else:
            return None
    return current
