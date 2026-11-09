from __future__ import annotations

from jsonhelpbot.utils.json_tools import dumps, loads_payload


def test_dumps_keeps_unicode():
    assert dumps({"text": "Привет"}) == '{\n  "text": "Привет"\n}'


def test_loads_payload_valid():
    payload = loads_payload('  {"type": "text", "text": "Hello"}  ')

    assert payload == {"type": "text", "text": "Hello"}


def test_loads_payload_requires_type():
    assert loads_payload('{"text": "Hello"}') is None


def test_loads_payload_rejects_array():
    assert loads_payload('[{"type": "text"}]') is None


def test_loads_payload_rejects_broken_json():
    assert loads_payload('{"type": "text",') is None


def test_loads_payload_rejects_plain_text():
    assert loads_payload("Hello") is None


def test_loads_payload_rejects_empty():
    assert loads_payload("") is None
    assert loads_payload(None) is None
