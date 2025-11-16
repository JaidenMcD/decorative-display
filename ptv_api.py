from hashlib import sha1
import hmac
from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timezone
import pytz

CITY_KEYWORDS = ["City", "Flinders", "Loop", "Southern Cross", "Parliament", "Richmond"]

load_dotenv()

devId = os.getenv("USER_ID")
key = os.getenv("API_KEY")
BASE_URL = "https://timetableapi.ptv.vic.gov.au"

tram_stop_id = os.getenv("TRAM_STOP_ID")
train_stop_id = os.getenv("TRAIN_STOP_ID")
tz = pytz.timezone(os.getenv("TIMEZONE"))

city_keywords = ["City", "Melbourne University", "Melbourne CBD", "Domain Interchange"]

def getUrl(endpoint: str) -> str:
    """Generate a properly signed PTV API URL."""
    request_str = endpoint + ('&' if '?' in endpoint else '?') + f"devid={devId}"
    signature = hmac.new(key.encode(), request_str.encode(), sha1).hexdigest()
    return f"{BASE_URL}{request_str}&signature={signature}"

def send_ptv_request(endpoint: str):
    """Send a GET request to the PTV API and return the JSON response."""
    url = getUrl(endpoint)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def parse_utc(ts):
    if ts is None:
        return None
    # Returns a datetime object in UTC
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


class MetroStop:
    def __init__(self, stop_id):
        self.stop_id = stop_id
        self.route_type = 0
        self.departures = []
    def get_departures(self):
        # Request next 2 per direction
        endpoint = f"/v3/departures/route_type/0/stop/{self.stop_id}?max_results=2&expand=direction"
        data = send_ptv_request(endpoint)

        departures = data["departures"]
        directions = data["directions"]

        # Group by direction_id
        grouped = {}
        for d in departures:
            did = d["direction_id"]
            grouped.setdefault(did, []).append(d)

        # Decide inbound/outbound based on direction name
        inbound = []
        outbound = []

        for did, deps in grouped.items():
            dname = directions[str(did)]["direction_name"]

            # pick which departures belong to inbound/outbound
            target = inbound if "city" in dname.lower() else outbound

            # Only take 2 departures max
            for dep in deps[:2]:
                # Use estimated if available, else scheduled
                t = dep.get("estimated_departure_utc") or dep.get("scheduled_departure_utc")
                target.append(parse_utc(t))

        # Ensure exactly two entries, pad with None if missing
        inbound = inbound[:2]
        outbound = outbound[:2]
        self.departures = [inbound, outbound]
    def returnDepartures(self):
        return self.departures