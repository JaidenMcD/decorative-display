from hashlib import sha1
import hmac
import binascii
from dotenv import load_dotenv
import os

load_dotenv()

devId = os.getenv("USER_ID")
key = os.getenv("API_KEY")

def getUrl(request):
    request = request + ('&' if ('?' in request) else '?')
    raw = f"{request}devid={devId}"
    hashed = hmac.new(key.encode('utf-8'), raw.encode('utf-8'), sha1)
    signature = hashed.hexdigest()
    return f"http://tst.timetableapi.ptv.vic.gov.au{raw}&signature={signature}"

print(getUrl('/v2/healthcheck'))