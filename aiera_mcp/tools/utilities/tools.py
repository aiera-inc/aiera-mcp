#!/usr/bin/env python3

"""Utility tools for Aiera MCP."""

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from .models import (
    GetCurrentDateTimeArgs,
    GetCurrentDateTimeResponse,
)

# Setup logging
logger = logging.getLogger(__name__)


async def get_current_datetime(
    args: GetCurrentDateTimeArgs,
) -> GetCurrentDateTimeResponse:
    """Get the current date and time in the specified timezone."""
    logger.info("tool called: get_current_datetime")

    try:
        # Get current datetime in the specified timezone
        tz = ZoneInfo(args.timezone)
        now = datetime.now(tz)

        # Get timezone abbreviation (EST/EDT, PST/PDT, etc.)
        tz_abbr = now.strftime("%Z")

        # Format the response
        return GetCurrentDateTimeResponse(
            current_datetime=now.strftime("%Y-%m-%dT%H:%M:%S"),
            current_date=now.strftime("%Y-%m-%d"),
            current_time=now.strftime("%H:%M:%S"),
            timezone=args.timezone,
            timezone_abbreviation=tz_abbr,
            unix_timestamp=int(now.timestamp()),
            day_of_week=now.strftime("%A"),
            instructions=[
                f"Current date/time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}",
                "Use the 'current_date' field (YYYY-MM-DD format) for date filtering in other tools",
                "All Aiera API dates are in Eastern Time (ET) by default",
                f"For date ranges, use dates before {now.strftime('%Y-%m-%d')} for historical data",
            ],
        )
    except Exception as e:
        logger.error(f"Failed to get current datetime: {e}")
        # Fallback to UTC if timezone is invalid
        now_utc = datetime.now(ZoneInfo("UTC"))
        return GetCurrentDateTimeResponse(
            current_datetime=now_utc.strftime("%Y-%m-%dT%H:%M:%S"),
            current_date=now_utc.strftime("%Y-%m-%d"),
            current_time=now_utc.strftime("%H:%M:%S"),
            timezone="UTC",
            timezone_abbreviation="UTC",
            unix_timestamp=int(now_utc.timestamp()),
            day_of_week=now_utc.strftime("%A"),
            instructions=[
                f"Current date/time (UTC): {now_utc.strftime('%Y-%m-%d %H:%M:%S UTC')}",
                "Use the 'current_date' field (YYYY-MM-DD format) for date filtering in other tools",
                f"Error with requested timezone '{args.timezone}', returned UTC instead",
            ],
        )
