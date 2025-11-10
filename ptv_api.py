from hashlib import sha1
import hmac
import binascii
from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timezone

load_dotenv()

devId = os.getenv("USER_ID")
key = os.getenv("API_KEY")
BASE_URL = "https://timetableapi.ptv.vic.gov.au"

tram_stop_id = os.getenv("TRAM_STOP_ID")
train_stop_id = os.getenv("TRAIN_STOP_ID")


def getUrl(endpoint: str) -> str:
    """Generate a properly signed PTV API URL."""
    request_str = endpoint + ('&' if '?' in endpoint else '?') + f"devid={devId}"
    signature = hmac.new(key.encode(), request_str.encode(), sha1).hexdigest()
    return f"{BASE_URL}{request_str}&signature={signature}"


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

    def get_departures(self, max_results=10):
        """Fetch departures from the PTV API for this tram stop."""
        endpoint = f"/v3/departures/route_type/1/stop/{self.stop_id}?max_results={max_results}"
        url = getUrl(endpoint)
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("departures", [])
        else:
            print(f"Error {response.status_code}: {response.text}")
            return []

    def _filter_and_next(self, departures, route_id=None, direction_id=None):
        """Helper: filter departures by route and direction, and get the soonest one."""
        now = datetime.now(timezone.utc)
        future = []
        for dep in departures:
            t = dep.get("estimated_departure_utc") or dep.get("scheduled_departure_utc")
            if not t:
                continue
            dt = datetime.fromisoformat(t.replace("Z", "+00:00"))
            if dt >= now:
                if (route_id is None or dep["route_id"] == route_id) and \
                   (direction_id is None or dep["direction_id"] == direction_id):
                    future.append((dt, dep))
        if not future:
            return None
        return sorted(future, key=lambda x: x[0])[0]  # soonest

    def get_next_city_tram(self):
        """Return the next tram to the city (either Route 5 or 64)."""
        deps = self.get_departures()
        return self._filter_and_next(deps, direction_id=None if not deps else None,
                                     route_id=None if not deps else None,
                                     )

    def get_next_city_tram(self):
        """Next tram to the city (Route 5 or 64)."""
        deps = self.get_departures()
        city_trams = [self._filter_and_next(deps, 1083, 17),
                      self._filter_and_next(deps, 909, 24)]
        city_trams = [c for c in city_trams if c]
        return min(city_trams, key=lambda x: x[0]) if city_trams else None

    def get_next_route5_outbound(self):
        """Next Route 5 tram leaving the city."""
        deps = self.get_departures()
        return self._filter_and_next(deps, 1083, 8)

    def get_next_route64_outbound(self):
        """Next Route 64 tram leaving the city."""
        deps = self.get_departures()
        return self._filter_and_next(deps, 909, 8)