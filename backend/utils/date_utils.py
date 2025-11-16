"""Date and time utilities."""

from datetime import datetime, timezone, timedelta
from typing import Optional


def now_utc() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def days_ago(days: int) -> datetime:
    """Get datetime N days ago from now."""
    return now_utc() - timedelta(days=days)


def format_iso(dt: Optional[datetime]) -> Optional[str]:
    """Format datetime to ISO 8601 string."""
    if dt is None:
        return None
    return dt.isoformat()
