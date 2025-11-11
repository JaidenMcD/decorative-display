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

def send_ptv_request(endpoint: str):
    """Send a GET request to the PTV API and return the JSON response."""
    url = getUrl(endpoint)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

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

    def get_departures(self, max_results=10):
        """Fetch departures from the PTV API for this tram stop."""
        endpoint = f"/v3/departures/route_type/{self.route_type}/stop/{self.stop_id}?max_results={max_results}"
        url = getUrl(endpoint)
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("departures", [])
        else:
            print(f"Error {response.status_code}: {response.text}")
            return []

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

        print(self.directions)
        return directions