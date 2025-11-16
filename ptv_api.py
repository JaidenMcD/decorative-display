from hashlib import sha1
import hmac
from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timezone
import pytz

CITY_KEYWORDS = ["City", "Flinders", "Loop", "Southern Cross", "Parliament", "Richmond"]
city_keywords = ["City", "Melbourne University", "Melbourne CBD", "Domain Interchange"]
def is_citybound(direction_name: str) -> bool:
    """Return True if this direction name looks like 'towards the city'."""
    if not direction_name:
        return False

    name = direction_name.lower()

    # Use both lists you've defined
    keywords = CITY_KEYWORDS + city_keywords
    return any(k.lower() in name for k in keywords)

load_dotenv()

devId = os.getenv("USER_ID")
key = os.getenv("API_KEY")
BASE_URL = "https://timetableapi.ptv.vic.gov.au"

tram_stop_id = os.getenv("TRAM_STOP_ID")
train_stop_id = os.getenv("TRAIN_STOP_ID")
tz = pytz.timezone(os.getenv("TIMEZONE"))



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
    
class TramStop:
    """
    Represents a tram stop that may be served by multiple routes. For each route_number we store up to 2 inbound
    and 2 outbound departures.
    """
    def __init__(self, stop_id):
        self.stop_id = stop_id
        self.route_type = 1       # 1 = tram
        # { route_number: { "inbound": [datetime, ...], "outbound": [datetime, ...] } }
        self.routes = {}

    def get_departures(self, max_results=40):
        """
        Populate self.routes with upcoming departures.

        Structure:
        {
          "5":  { "inbound": [dt1, dt2], "outbound": [dt3, dt4] },
          "64": { "inbound": [...],      "outbound": [...]      },
          ...
        }
        """
        endpoint = (
        f"/v3/departures/route_type/{self.route_type}/stop/{self.stop_id}"
        f"?max_results={max_results}&expand=all"
        )
        data = send_ptv_request(endpoint)

        if not data:
            self.routes = {}
            return

        departures = data.get("departures", [])
        routes_info = data.get("routes", {})
        directions = data.get("directions", {})

        grouped = {}

        for dep in departures:
            route_id = dep.get("route_id")
            direction_id = dep.get("direction_id")

            # Look up route + direction metadata (keys are usually strings)
            route_obj = routes_info.get(str(route_id), routes_info.get(route_id))
            dir_obj = directions.get(str(direction_id), directions.get(direction_id))

            if route_obj is None or dir_obj is None:
                continue

            route_number = route_obj.get("route_number") or str(route_id)

            # Pick estimated time first, then scheduled
            t_str = dep.get("estimated_departure_utc") or dep.get("scheduled_departure_utc")
            dep_time = parse_utc(t_str)
            if dep_time is None:
                continue

            direction_name = dir_obj.get("direction_name", "")
            bound_key = "inbound" if is_citybound(direction_name) else "outbound"

            route_entry = grouped.setdefault(
                route_number,
                {"inbound": [], "outbound": []}
            )
            route_entry[bound_key].append(dep_time)

        # Sort by time and keep only the next 2 for each direction
        for route_number, entry in grouped.items():
            entry["inbound"] = sorted(entry["inbound"])[:2]
            entry["outbound"] = sorted(entry["outbound"])[:2]

        self.routes = grouped

    def returnDepartures(self):
        """Return the internal structure of routes -> inbound/outbound lists."""
        return self.routes