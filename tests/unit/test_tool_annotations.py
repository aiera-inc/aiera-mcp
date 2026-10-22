"""Every tool advertises explicit readOnlyHint / destructiveHint / openWorldHint
booleans (CORE-4805). OpenAI's MCP host flags tools whose annotations leave any
of the three unset, so the registry carries all three and the server emits them."""

import pytest

from aiera_mcp.server import tool_annotations_from_config, tool_from_config
from aiera_mcp.tools.registry import TOOL_REGISTRY

HINT_KEYS = ("read_only", "destructive", "open_world")


@pytest.mark.parametrize("tool_name", sorted(TOOL_REGISTRY))
def test_registry_entry_declares_all_three_hints_as_bools(tool_name):
    cfg = TOOL_REGISTRY[tool_name]
    for key in HINT_KEYS:
        assert key in cfg, f"{tool_name} is missing {key!r}"
        assert isinstance(cfg[key], bool), f"{tool_name}.{key} must be a bool"


def test_only_web_search_is_open_world():
    """Every other tool talks to Aiera's own API: a closed world."""
    assert {name for name, cfg in TOOL_REGISTRY.items() if cfg["open_world"]} == {
        "trusted_web_search"
    }


@pytest.mark.parametrize("tool_name", sorted(TOOL_REGISTRY))
def test_server_tool_carries_explicit_annotations(tool_name):
    tool = tool_from_config(tool_name, TOOL_REGISTRY[tool_name])
    ann = tool.annotations
    assert ann is not None
    assert isinstance(ann.readOnlyHint, bool)
    assert isinstance(ann.destructiveHint, bool)
    assert isinstance(ann.openWorldHint, bool)
    assert ann.openWorldHint is (tool_name == "trusted_web_search")
    assert ann.title == TOOL_REGISTRY[tool_name].get("display_name")


def test_annotations_default_to_closed_world_when_flag_absent():
    ann = tool_annotations_from_config({"display_name": "X"})
    assert (ann.readOnlyHint, ann.destructiveHint, ann.openWorldHint) == (
        True,
        False,
        False,
    )
