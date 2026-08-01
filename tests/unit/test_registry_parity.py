#!/usr/bin/env python3

"""Guards that the hand-maintained tool lists in aiera_mcp/__init__.py stay in
sync with TOOL_REGISTRY (the single source of truth).

These catch the class of drift where a tool is added to the registry but not to
AVAILABLE_TOOLS / a tool group (or vice versa) — which silently omits it from
anything that iterates those convenience lists.
"""

import pytest

import aiera_mcp
from aiera_mcp import (
    AVAILABLE_TOOLS,
    EVENT_TOOLS,
    FILING_TOOLS,
    EQUITY_TOOLS,
    INDEX_WATCHLIST_TOOLS,
    COMPANY_DOC_TOOLS,
    THIRD_BRIDGE_TOOLS,
    RESEARCH_TOOLS,
    SEARCH_TOOLS,
    WEB_TOOLS,
    COMMON_TOOLS,
)
from aiera_mcp.tools.registry import TOOL_REGISTRY

ALL_GROUPS = [
    EVENT_TOOLS,
    FILING_TOOLS,
    EQUITY_TOOLS,
    INDEX_WATCHLIST_TOOLS,
    COMPANY_DOC_TOOLS,
    THIRD_BRIDGE_TOOLS,
    RESEARCH_TOOLS,
    SEARCH_TOOLS,
    WEB_TOOLS,
    COMMON_TOOLS,
]


@pytest.mark.unit
class TestRegistryParity:
    def test_available_tools_matches_registry(self):
        registry = set(TOOL_REGISTRY.keys())
        available = set(AVAILABLE_TOOLS)
        assert available == registry, (
            f"AVAILABLE_TOOLS drifted from TOOL_REGISTRY. "
            f"Missing from AVAILABLE_TOOLS: {sorted(registry - available)}; "
            f"extra in AVAILABLE_TOOLS: {sorted(available - registry)}"
        )

    def test_available_tools_has_no_duplicates(self):
        assert len(AVAILABLE_TOOLS) == len(set(AVAILABLE_TOOLS))

    def test_tool_groups_cover_registry_exactly(self):
        grouped = [t for group in ALL_GROUPS for t in group]
        registry = set(TOOL_REGISTRY.keys())
        assert set(grouped) == registry, (
            f"Tool groups drifted from TOOL_REGISTRY. "
            f"Missing from groups: {sorted(registry - set(grouped))}; "
            f"extra in groups: {sorted(set(grouped) - registry)}"
        )

    def test_tool_groups_are_disjoint(self):
        # A tool should live in exactly one convenience group.
        grouped = [t for group in ALL_GROUPS for t in group]
        dupes = sorted({t for t in grouped if grouped.count(t) > 1})
        assert not dupes, f"tools appear in multiple groups: {dupes}"

    def test_every_exported_tool_is_importable(self):
        for name in AVAILABLE_TOOLS:
            assert hasattr(aiera_mcp, name), f"{name} is in AVAILABLE_TOOLS but not importable from aiera_mcp"
            assert name in aiera_mcp.__all__, f"{name} is not exported in aiera_mcp.__all__"
