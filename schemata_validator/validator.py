"""Nostr JSON schema validator."""

import copy
from typing import Any, Optional

import jsonschema

import schemata

from schemata_validator.types import ValidationError, ValidationResult, Subject
from schemata_validator.additional_props import collect_additional_props
from schemata_validator.error_messages import enrich_message


def _strip_nested_ids(value: Any, depth: int = 0) -> Any:
    if isinstance(value, dict):
        if depth > 0:
            value.pop("$id", None)
        for k in value:
            value[k] = _strip_nested_ids(value[k], depth + 1)
    elif isinstance(value, list):
        for i, item in enumerate(value):
            value[i] = _strip_nested_ids(item, depth + 1)
    return value


def validate(schema: dict, data: Any) -> ValidationResult:
    """Validate data against a JSON schema."""
    schema_copy = copy.deepcopy(schema)
    _strip_nested_ids(schema_copy, 0)

    try:
        validator = jsonschema.Draft7Validator(schema_copy)
    except jsonschema.SchemaError as e:
        return ValidationResult(
            valid=False,
            errors=[ValidationError(keyword="compilation", message=str(e))],
        )

    errors = []
    for error in validator.iter_errors(data):
        msg = enrich_message(schema_copy, list(error.absolute_schema_path), error.validator, str(error.message))
        errors.append(ValidationError(
            instance_path="/".join(str(p) for p in error.absolute_path) if error.absolute_path else "",
            keyword=error.validator or "",
            message=msg,
            schema_path="/".join(str(p) for p in error.absolute_schema_path) if error.absolute_schema_path else "",
        ))

    warnings = collect_additional_props(schema, data, "")

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


def validate_note(event: dict) -> ValidationResult:
    """Validate a Nostr event by kind."""
    kind = event.get("kind")
    if kind is None:
        return ValidationResult(
            valid=False,
            errors=[ValidationError(keyword="note", message="Event missing 'kind' field")],
        )

    key = f"kind{kind}Schema"
    schema = schemata.get(key)
    if schema is None:
        return ValidationResult(
            valid=False,
            warnings=[ValidationError(keyword="note", message=f"No schema found for kind {kind}")],
        )
    return validate(schema, event)


def validate_nip11(doc: dict) -> ValidationResult:
    """Validate a NIP-11 relay information document."""
    schema = schemata.get("nip11Schema")
    if schema is None:
        return ValidationResult(
            valid=False,
            errors=[ValidationError(keyword="nip11", message="nip11Schema not found")],
        )
    return validate(schema, doc)


def validate_message(msg: Any, subject: Subject, slug: str) -> ValidationResult:
    """Validate a protocol message (relay or client)."""
    key = f"{subject.value}{slug.capitalize()}Schema"
    schema = schemata.get(key)
    if schema is None:
        return ValidationResult(
            valid=False,
            warnings=[ValidationError(keyword="message", message=f"No schema found for {subject.value} {slug}")],
        )
    return validate(schema, msg)


def get_schema(key: str) -> Optional[dict]:
    """Look up a schema by key."""
    return schemata.get(key)
