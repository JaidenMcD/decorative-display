from hashlib import sha1
import hmac
import binascii
from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timezone
import pytz

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


def parse_utc_to_local(utc_str, tz):
    """Convert ISO UTC string (with 'Z') to local timezone-aware datetime."""
    if not utc_str:
        return None
    # Convert string → datetime
    utc_dt = datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
    # Convert UTC → local timezone
    return utc_dt.astimezone(tz)


def get_tram_departures():
    """
    Perform GET request on /v3/departures/route_type/{route_type}/stop/{stop_id}
    """
    endpoint = f"/v3/departures/route_type/1/stop/{tram_stop_id}?expand=Route,Direction&max_results=5"
    url = getUrl(endpoint)
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None
    
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
    

class TramStop:
    def __init__(self, stop_id):
        self.stop_id = stop_id
        self.directions = []
        self.route_type = 1
        self.next_departures = []

    def get_departures(self, max_results=2):
        """Fetch up to `max_results` departures per direction for this tram stop."""
        if not self.directions:
            print("Populating stop details first...")
            self.populate_stop()

        self.next_departures = []  # clear previous departures each refresh
        run_ids = []

        for direction in self.directions:
            for route_id in direction["route_ids"]:
                departures = send_ptv_request(
                    f"/v3/departures/route_type/{self.route_type}/stop/{self.stop_id}/route/{route_id}?max_results={max_results}"
                )
                for departure in departures.get("departures", []):
                    run_id = departure.get("run_id")
                    if run_id in run_ids:
                        continue
                    run_ids.append(run_id)

                    # Get estimated or scheduled departure time
                    est_utc = departure.get("estimated_departure_utc") or departure.get("scheduled_departure_utc")
                    if not est_utc:
                        continue

                    # Convert to datetime
                    est_dt = parse_utc_to_local(est_utc, tz)

                    new_departure = {
                        "route_id": departure.get("route_id"),
                        "direction_id": departure.get("direction_id"),
                        "scheduled_departure_utc": parse_utc_to_local(departure.get("scheduled_departure_utc"), tz),
                        "estimated_departure_utc": parse_utc_to_local(departure.get("estimated_departure_utc"), tz),
                        "run_id": run_id,
                        "time": est_dt,
                    }

                    self.next_departures.append(new_departure)

        # Sort all departures by time
        self.next_departures.sort(
            key=lambda d: d["estimated_departure_utc"] or d["scheduled_departure_utc"]
        )

    def return_departures(self):
        if not self.next_departures:
            return []

        now = datetime.now(tz)
        directions_grouped = {}
        for dep in self.next_departures:
            directions_grouped.setdefault(dep["direction_id"], []).append(dep)

        results = []
        for direction_id, deps in directions_grouped.items():
            deps.sort(key=lambda d: d["estimated_departure_utc"] or d["scheduled_departure_utc"])

            direction_name = next(
                (d["direction_name"] for d in self.directions if d["direction_id"] == direction_id),
                "Unknown direction"
            )

            is_city = any(kw.lower() in direction_name.lower() for kw in city_keywords)
            label = "city" if is_city else direction_name

            countdowns = []
            for dep in deps[:2]:
                dep_time = dep["estimated_departure_utc"] or dep["scheduled_departure_utc"]
                if isinstance(dep_time, str):
                    dep_time = parse_utc_to_local(dep_time, tz)

                delta = int((dep_time - now).total_seconds())
                minutes, seconds = divmod(max(delta, 0), 60)
                countdowns.append(f"{minutes:02d}:{seconds:02d}")

            results.append({
                "direction": label,
                "countdowns": countdowns
            })

        return results

    def populate_stop(self):
        """Fetch and populate tram stop details from the PTV API."""
        self.directions = [] 

        # Step 1: Get direction IDs from departures
        directions = []
        departures = send_ptv_request(f"/v3/departures/route_type/{self.route_type}/stop/{self.stop_id}?max_results=5")
        if departures:
            for departure in departures.get("departures", []):
                id = departure.get("direction_id")
                if id and id not in directions:
                    directions.append(id)
        else:
            return []

        # Step 2: For each direction, fetch and merge data
        for direction_id in directions:
            response = send_ptv_request(f"/v3/directions/{direction_id}")
            for direction in response.get("directions", []):
                if direction.get("route_type") != self.route_type:
                    continue

                new_direction = {
                    "direction_id": direction.get("direction_id"),
                    "direction_name": direction.get("direction_name"),
                    "route_ids": [direction.get("route_id")]
                }

                # --- Check for duplicates before appending ---
                found = False
                for existing in self.directions:
                    if existing["direction_id"] == new_direction["direction_id"]:
                        if new_direction["route_ids"][0] not in existing["route_ids"]:
                            existing["route_ids"].append(new_direction["route_ids"][0])
                        found = True
                        break

                if not found:
                    self.directions.append(new_direction)

        return directions