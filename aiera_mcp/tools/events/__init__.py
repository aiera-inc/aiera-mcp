#!/usr/bin/env python3

"""Events domain for Aiera MCP."""

from .tools import find_events, get_event, get_upcoming_events
from .models import (
    FindEventsArgs,
    GetEventArgs,
    GetUpcomingEventsArgs,
    FindEventsResponse,
    GetEventResponse,
    GetUpcomingEventsResponse,
    EventItem,
    EventDetails,
    EventType,
)

__all__ = [
    # Tools
    "find_events",
    "get_event",
    "get_upcoming_events",
    # Parameter models
    "FindEventsArgs",
    "GetEventArgs",
    "GetUpcomingEventsArgs",
    # Response models
    "FindEventsResponse",
    "GetEventResponse",
    "GetUpcomingEventsResponse",
    # Data models
    "EventItem",
    "EventDetails",
    "EventType",
]
