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
    raw = request+'devid={0}'.format(devId)
    hashed = hmac.new(key, raw, sha1)
    signature = hashed.hexdigest()
    return 'http://tst.timetableapi.ptv.vic.gov.au'+raw+'&signature={1}'.format(devId, signature)

print(getUrl('/v2/healthcheck'))
