# schemata-validator-py

[![Test](https://github.com/nostrability/schemata-validator-py/actions/workflows/test.yml/badge.svg)](https://github.com/nostrability/schemata-validator-py/actions/workflows/test.yml)

Python validator for [Nostr](https://nostr.com/) protocol JSON schemas. Built on top of [`schemata-py`](https://github.com/nostrability/schemata-py) and [`jsonschema`](https://python-jsonschema.readthedocs.io/).

## When to use this

JSON Schema validation is [not suited for runtime hot paths](https://github.com/nostrability/schemata#what-is-it-not-good-for). Use this in **CI and integration tests**.

## Usage

```python
from schemata_validator import validate_note

event = {"id": "aa...", "pubkey": "bb...", "created_at": 1700000000, "kind": 1, "tags": [], "content": "hello", "sig": "cc..."}
result = validate_note(event)
assert result.valid, result.errors
```

## License

GPL-3.0-or-later
