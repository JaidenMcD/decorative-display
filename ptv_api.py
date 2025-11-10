from hashlib import sha1
import hmac
import binascii
from dotenv import load_dotenv
import os

load_dotenv()

devId = os.getenv("USER_ID")
key = os.getenv("API_KEY")
BASE_URL = "http://timetableapi.ptv.vic.gov.au"


def getUrl(endpoint: str) -> str:
    """Generate a properly signed PTV API URL."""
    request_str = endpoint + ('&' if '?' in endpoint else '?') + f"devid={devId}"
    signature = hmac.new(key.encode(), request_str.encode(), sha1).hexdigest().upper()
    return f"{BASE_URL}{request_str}&signature={signature}"

print(getUrl('/v2/healthcheck'))