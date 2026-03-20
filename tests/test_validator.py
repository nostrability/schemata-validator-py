from schemata_validator import validate, validate_note, validate_nip11, validate_message, get_schema, Subject


def _hex(c, n=64):
    return c * n


def test_kind1_validates():
    event = {
        "id": _hex("a"), "pubkey": _hex("b"), "created_at": 1700000000,
        "kind": 1, "tags": [], "content": "hello world", "sig": _hex("c", 128),
    }
    result = validate_note(event)
    assert result.valid, f"errors: {[e.message for e in result.errors]}"


def test_wrong_kind_fails():
    event = {
        "id": _hex("a"), "pubkey": _hex("b"), "created_at": 1700000000,
        "kind": 1, "tags": [], "content": "hello", "sig": _hex("c", 128),
    }
    schema = get_schema("kind0Schema")
    assert schema is not None
    result = validate(schema, event)
    assert not result.valid


def test_missing_pubkey_fails():
    event = {"kind": 1, "content": "hello"}
    result = validate_note(event)
    assert not result.valid


def test_p_tag_validates():
    schema = get_schema("pTagSchema")
    assert schema is not None
    result = validate(schema, ["p", _hex("a")])
    assert result.valid, f"errors: {[e.message for e in result.errors]}"


def test_nip11_validates():
    doc = {"name": "Test Relay", "supported_nips": [1, 11]}
    result = validate_nip11(doc)
    assert result.valid, f"errors: {[e.message for e in result.errors]}"


def test_unknown_kind_warning():
    event = {
        "id": _hex("a"), "pubkey": _hex("b"), "created_at": 1700000000,
        "kind": 99999, "tags": [], "content": "", "sig": _hex("c", 128),
    }
    result = validate_note(event)
    assert not result.valid
    assert any("No schema found" in w.message for w in result.warnings)


def test_additional_props_warning():
    schema = {"type": "object", "properties": {"name": {"type": "string"}}}
    data = {"name": "Alice", "extra": "surprise"}
    result = validate(schema, data)
    assert result.valid
    assert any("extra" in w.message for w in result.warnings)
