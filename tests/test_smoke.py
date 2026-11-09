from __future__ import annotations

import importlib

import pytest

MODULES = (
    "jsonhelpbot.config",
    "jsonhelpbot.main",
    "jsonhelpbot.handlers.common",
    "jsonhelpbot.handlers.convert",
    "jsonhelpbot.serializers.json_to_message",
    "jsonhelpbot.serializers.message_to_json",
    "jsonhelpbot.serializers.schema",
    "jsonhelpbot.utils.json_tools",
    "jsonhelpbot.utils.replies",
)


@pytest.mark.parametrize("module_name", MODULES)
def test_module_is_importable(module_name):
    assert importlib.import_module(module_name) is not None
