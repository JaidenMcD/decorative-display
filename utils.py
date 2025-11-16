from datetime import datetime, timezone
def to_countdown(dep_time):
    """Return minutes + seconds remaining to a departure."""
    if dep_time is None:
        return None

    now = datetime.now(timezone.utc)       # current time in UTC
    diff = dep_time - now

    # If already passed, return "now"
    if diff.total_seconds() <= 0:
        return "now"

    mins = int(diff.total_seconds() // 60)
    secs = int(diff.total_seconds() % 60)
    return f"{mins} m {secs} s"