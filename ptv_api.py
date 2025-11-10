from hashlib import sha1
import hmac
import binascii
from dotenv import load_dotenv
import os
import requests

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
    

    def get_departures(self, max_results=5):
        endpoint = f"/v3/departures/route_type/1/stop/{self.stop_id}?max_results={max_results}"
        url = getUrl(endpoint)
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    
