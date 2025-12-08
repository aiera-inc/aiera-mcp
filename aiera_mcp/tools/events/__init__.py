#!/usr/bin/env python3

"""Events domain for Aiera MCP."""

from .tools import find_events, find_conferences, get_event, get_upcoming_events
from .models import (
    FindEventsArgs,
    FindConferencesArgs,
    GetEventArgs,
    GetUpcomingEventsArgs,
    FindEventsResponse,
    FindConferencesResponse,
    GetEventResponse,
    GetUpcomingEventsResponse,
    EventItem,
    EventDetails,
    EventType,
    TranscriptItem,
    EstimatedEventItem,
    UpcomingActualEventItem,
    EstimateInfo,
    ActualInfo,
)

__all__ = [
    # Tools
    "find_events",
    "find_conferences",
    "get_event",
    "get_upcoming_events",
    # Parameter models
    "FindEventsArgs",
    "FindConferencesArgs",
    "GetEventArgs",
    "GetUpcomingEventsArgs",
    # Response models
    "FindEventsResponse",
    "FindConferencesResponse",
    "GetEventResponse",
    "GetUpcomingEventsResponse",
    # Data models
    "EventItem",
    "EventDetails",
    "EventType",
    "TranscriptItem",
    "EstimatedEventItem",
    "UpcomingActualEventItem",
    "EstimateInfo",
    "ActualInfo",
]
