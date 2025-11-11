from datetime import datetime
import pytz

def parse_utc_to_local(utc_str, tz):
    if not utc_str:
        return None
    utc_dt = datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
    return utc_dt.astimezone(tz)

def format_countdown(dep_time, now):
    delta = int((dep_time - now).total_seconds())
    minutes, seconds = divmod(max(delta, 0), 60)
    return f"{minutes:02d}:{seconds:02d}"