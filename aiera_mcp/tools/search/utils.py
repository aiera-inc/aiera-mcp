#!/usr/bin/env python3

"""Utility functions for Aiera search tools."""

from typing import List


def correct_provided_ids(ids_str: str) -> List[int]:
    """Convert comma-separated ID string to list of integers."""
    if not ids_str or not ids_str.strip():
        return []

    ids = []
    for id_str in ids_str.split(","):
        id_str = id_str.strip()
        if id_str:
            try:
                ids.append(int(id_str))
            except ValueError:
                # Skip invalid IDs
                continue
    return ids


def correct_provided_types(types_str: str) -> List[str]:
    """Convert comma-separated types string to list of strings."""
    if not types_str or not types_str.strip():
        return []

    types = []
    for type_str in types_str.split(","):
        type_str = type_str.strip()
        if type_str:
            types.append(type_str)
    return types


def correct_event_type(event_type: str) -> str:
    """Normalize event type string."""
    if not event_type:
        return ""

    # Map common variations to canonical forms
    event_type = event_type.strip().lower()
    type_mappings = {
        "earning": "earnings",
        "presentation": "presentation",
        "conference": "presentation",
        "shareholder_meeting": "shareholder_meeting",
        "annual_meeting": "shareholder_meeting",
        "investor_meeting": "investor_meeting",
        "special_situation": "special_situation",
        "merger": "special_situation",
        "acquisition": "special_situation",
    }

    return type_mappings.get(event_type, event_type)
