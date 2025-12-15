#!/usr/bin/env python3

"""Utility tools domain models for Aiera MCP."""

from pydantic import BaseModel, Field
from typing import Optional


class GetCurrentDateTimeArgs(BaseModel):
    """Get the current date and time in Eastern Time (ET) zone. Use this tool whenever you need to know what date or time it is right now. This is especially useful when filtering data by date ranges or determining if events are upcoming or past."""

    timezone: Optional[str] = Field(
        default="America/New_York",
        description="Timezone for the current date/time. Defaults to 'America/New_York' (ET). Other options: 'UTC', 'America/Los_Angeles' (PT), 'America/Chicago' (CT), etc.",
    )


class GetCurrentDateTimeResponse(BaseModel):
    """Response containing current date and time information."""

    current_datetime: str = Field(
        description="Current date and time in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)"
    )
    current_date: str = Field(description="Current date in YYYY-MM-DD format")
    current_time: str = Field(description="Current time in HH:MM:SS format")
    timezone: str = Field(description="Timezone used for the date/time")
    timezone_abbreviation: str = Field(
        description="Timezone abbreviation (e.g., 'EST', 'EDT', 'UTC')"
    )
    unix_timestamp: int = Field(description="Unix timestamp (seconds since epoch)")
    day_of_week: str = Field(description="Day of the week (e.g., 'Monday', 'Tuesday')")
    instructions: list[str] = Field(
        default_factory=list,
        description="Instructions for using the date/time information",
    )
