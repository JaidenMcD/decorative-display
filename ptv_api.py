from hashlib import sha1
import hmac
import binascii
from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timezone
import json

load_dotenv()

devId = os.getenv("USER_ID")
key = os.getenv("API_KEY")
BASE_URL = "http://timetableapi.ptv.vic.gov.au"

tram_stop_id = os.getenv("TRAM_STOP_ID")
train_stop_id = os.getenv("TRAIN_STOP_ID")


def getUrl(endpoint: str) -> str:
    """Generate a properly signed PTV API URL."""
    request_str = endpoint + ('&' if '?' in endpoint else '?') + f"devid={devId}"
    signature = hmac.new(key.encode(), request_str.encode(), sha1).hexdigest().upper()
    return f"{BASE_URL}{request_str}&signature={signature}"


def get_tram_departures():
    """
    Perform GET request on /v3/departures/route_type/{route_type}/stop/{stop_id}
    """
    endpoint = f"/v3/departures/route_type/1/stop/{tram_stop_id}"
    url = getUrl(endpoint)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None
    
def get_tram_departures(max_results: int = 5):
    """
    Calls /v3/departures/route_type/{route_type}/stop/{stop_id}
    and returns parsed next departure.
    """
    endpoint = f"/v3/departures/route_type/1/stop/{tram_stop_id}?max_results={max_results}"
    url = getUrl(endpoint)
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    # Parse departures
    now = datetime.now(timezone.utc)
    future_departures = []
    for dep in data.get("departures", []):
        t = dep.get("estimated_departure_utc") or dep.get("scheduled_departure_utc")
        if t:
            dt = datetime.fromisoformat(t.replace("Z", "+00:00"))
            if dt > now:
                future_departures.append((dt, dep))

    if not future_departures:
        print("No upcoming departures found.")
        return None

    # Sort and select next one
    next_dep_time, next_dep = sorted(future_departures, key=lambda x: x[0])[0]
    route_id = next_dep["route_id"]
    direction_id = next_dep["direction_id"]

    print("Next Departure:")
    print(f"  Route ID: {route_id}")
    print(f"  Direction ID: {direction_id}")
    print(f"  Scheduled: {next_dep_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")

    return next_dep
    
def get_train_departures():
    """
    Perform GET request on /v3/departures/route_type/{route_type}/stop/{stop_id}
    """
    endpoint = f"/v3/departures/route_type/0/stop/{train_stop_id}"
    url = getUrl(endpoint)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None