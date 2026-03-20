"""Additional properties detection — warnings, not errors."""

import re
from typing import Any

from schemata_validator.types import ValidationError


def collect_additional_props(schema: Any, data: Any, path: str) -> list[ValidationError]:
    if not isinstance(data, dict) or not isinstance(schema, dict):
        return []
    if schema.get("type") != "object":
        return []
    if schema.get("additionalProperties") is False:
        return []

    warnings = []
    allowed = set()

    props = schema.get("properties", {})
    if isinstance(props, dict):
        allowed.update(props.keys())

    patterns = schema.get("patternProperties", {})
    if isinstance(patterns, dict):
        for pattern in patterns:
            try:
                compiled = re.compile(pattern)
                for key in data:
                    if compiled.search(key):
                        allowed.add(key)
            except re.error:
                pass

    for key in data:
        if key not in allowed:
            warnings.append(ValidationError(
                instance_path=path,
                keyword="additionalProperties",
                message=f'additional property "{key}" exists',
            ))

    if isinstance(props, dict):
        for prop, prop_schema in props.items():
            if prop in data and isinstance(data[prop], dict):
                child_path = f"{path}/{prop}"
                warnings.extend(collect_additional_props(prop_schema, data[prop], child_path))

    return warnings
