from datetime import datetime, timezone

def to_countdown(dep_time):
    """Return minutes + seconds remaining to a departure."""
    if dep_time is None:
        return None

    now = datetime.now(timezone.utc)
    diff = dep_time - now
    secs_total = diff.total_seconds()

    # If already passed OR under 30 seconds: treat as NOW
    if secs_total <= 30:
        return "now"

    mins = int(secs_total // 60)
    secs = int(secs_total % 60)
    return f"{mins} m {secs} s"