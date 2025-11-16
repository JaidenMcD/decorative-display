# -*- coding: utf-8 -*-
from hashlib import sha1
import hmac
import os
import requests
from datetime import datetime, timedelta
import pytz
import json

# ---------- Replace pathlib with Python-2.7 safe paths ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, "cache")
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

CACHE_FILE = os.path.join(CACHE_DIR, "stops.json")
CACHE_EXPIRY_DAYS = 7


# ---------- Python-2.7 safe timestamp helpers ----------
def _parse_iso(dt_str):
    """
    Python 2.7 does NOT have datetime.fromisoformat.
    Accepts: "2025-02-21T12:34:00Z" or with +00:00
    """
    if dt_str is None:
        return None

    dt_str = dt_str.replace("Z", "+00:00")

    # Remove colon in timezone "+00:00" → "+0000"
    if dt_str.endswith("+00:00") or dt_str.endswith("-00:00"):
        dt_str = dt_str[:-3] + dt_str[-2:]

    try:
        return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S%z")
    except Exception:
        try:
            return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S%Z")
        except Exception:
            return None


def _now_with_tz(tz):
    """Python 2.7 safe 'now' with timezone."""
    return datetime.now(tz)


# ---------- Cache load/save ----------
def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_cache(data):
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print("Warning: failed to save cache ({})".format(e))


# ---------- ENV VARIABLES ----------
devId = os.getenv("USER_ID")
key = os.getenv("API_KEY")
BASE_URL = "https://timetableapi.ptv.vic.gov.au"

tram_stop_id = os.getenv("TRAM_STOP_ID")
train_stop_id = os.getenv("TRAIN_STOP_ID")

tz_str = os.getenv("TIMEZONE")
tz = pytz.timezone(tz_str if tz_str else "Australia/Melbourne")

city_keywords = ["City", "Melbourne University", "Melbourne CBD", "Domain Interchange"]


# ---------- URL signing (Python 2 safe) ----------
def getUrl(endpoint):
    request_str = endpoint + ('&' if '?' in endpoint else '?') + "devid={}".format(devId)

    # Python 2.7: env vars may be unicode → ensure bytes
    key_bytes = key.encode('utf-8') if isinstance(key, unicode) else key
    req_bytes = request_str.encode('utf-8') if isinstance(request_str, unicode) else request_str

    signature = hmac.new(key_bytes, req_bytes, sha1).hexdigest()

    return "{}{}&signature={}".format(BASE_URL, request_str, signature)


def send_ptv_request(endpoint):
    url = getUrl(endpoint)
    try:
        response = requests.get(url)
    except Exception as e:
        print("Request error: {}".format(e))
        return None

    if response.status_code == 200:
        return response.json()
    else:
        print("Error {}: {}".format(response.status_code, response.text))
        return None


# ---------- Route Info ----------
def get_route_info(route_id):
    cache = load_cache()
    routes = cache.get("routes", {})

    entry = routes.get(str(route_id))
    if entry:
        ts = _parse_iso(entry.get("timestamp"))
        if ts and (datetime.now() - ts < timedelta(days=CACHE_EXPIRY_DAYS)):
            return entry["data"]

    data = send_ptv_request("/v3/routes/{}".format(route_id))
    if data and "route" in data:
        route = data["route"]
        route_info = {
            "route_name": route.get("route_name"),
            "route_number": route.get("route_number")
        }

        cache.setdefault("routes", {})
        cache["routes"][str(route_id)] = {
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "data": route_info
        }
        save_cache(cache)
        print("Cached route {}".format(route_id))
        return route_info

    return {"route_name": None, "route_number": None}


# ---------- Time conversion ----------
def parse_utc_to_local(utc_str, tz):
    dt = _parse_iso(utc_str)
    if dt is None:
        return None
    return dt.astimezone(tz)


# ---------- Simple API wrappers ----------
def get_tram_departures():
    endpoint = "/v3/departures/route_type/1/stop/{}?expand=Route,Direction&max_results=5".format(tram_stop_id)
    return send_ptv_request(endpoint)


def get_train_departures():
    endpoint = "/v3/departures/route_type/0/stop/{}".format(train_stop_id)
    return send_ptv_request(endpoint)


# ---------- STOP CLASS ----------
class Stop(object):
    def __init__(self, stop_id, route_type):
        self.stop_id = stop_id
        self.route_type = route_type
        self.directions = []
        self.next_departures = []
        self.route_cache = {}

    # -------------------------------------------
    # FETCH DEPARTURES
    # -------------------------------------------
    def get_departures(self, max_results=2):
        if not self.directions:
            print("Populating stop details first...")
            self.populate_stop()

        self.next_departures = []
        run_ids = []

        for direction in self.directions:
            for route_id in direction["route_ids"]:
                departures = send_ptv_request(
                    "/v3/departures/route_type/{}/stop/{}/route/{}?max_results={}".format(
                        self.route_type, self.stop_id, route_id, max_results
                    )
                )
                if not departures:
                    continue

                for departure in departures.get("departures", []):
                    run_id = departure.get("run_id")
                    if run_id in run_ids:
                        continue
                    run_ids.append(run_id)

                    est_utc = departure.get("estimated_departure_utc") or departure.get("scheduled_departure_utc")
                    if not est_utc:
                        continue

                    est_dt = parse_utc_to_local(est_utc, tz)

                    new_dep = {
                        "route_id": departure.get("route_id"),
                        "direction_id": departure.get("direction_id"),
                        "scheduled_departure_utc": parse_utc_to_local(departure.get("scheduled_departure_utc"), tz),
                        "estimated_departure_utc": parse_utc_to_local(departure.get("estimated_departure_utc"), tz),
                        "run_id": run_id,
                        "time": est_dt
                    }
                    self.next_departures.append(new_dep)

        self.next_departures.sort(
            key=lambda d: d["estimated_departure_utc"] or d["scheduled_departure_utc"]
        )

    # -------------------------------------------
    # CONVERT DEPARTURES FOR UI
    # -------------------------------------------
    def return_departures(self):
        if not self.next_departures:
            return []

        now = _now_with_tz(tz)
        groups = {}

        for dep in self.next_departures:
            groups.setdefault(dep["direction_id"], []).append(dep)

        results = []

        for direction_id, deps in groups.items():
            deps.sort(key=lambda d: d["estimated_departure_utc"] or d["scheduled_departure_utc"])

            direction_name = "Unknown direction"
            for d in self.directions:
                if d["direction_id"] == direction_id:
                    direction_name = d["direction_name"]
                    break

            is_city = any(kw.lower() in direction_name.lower() for kw in city_keywords)
            label = "city" if is_city else direction_name

            route_id = deps[0].get("route_id")

            if route_id not in self.route_cache:
                self.route_cache[route_id] = get_route_info(route_id)

            route_number = self.route_cache[route_id].get("route_number") or "?"

            countdowns = []
            for dep in deps[:2]:
                dt = dep["estimated_departure_utc"] or dep["scheduled_departure_utc"]
                delta = int((dt - now).total_seconds())
                minutes, seconds = divmod(max(delta, 0), 60)
                countdowns.append("{:02d}:{:02d}".format(minutes, seconds))

            results.append({
                "direction": label,
                "route_id": route_id,
                "route_number": route_number,
                "countdowns": countdowns
            })

        return results

    # -------------------------------------------
    # POPULATE STOP (CACHE OR API)
    # -------------------------------------------
    def populate_stop(self):
        self.directions = []

        # Try cache
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as f:
                cache = json.load(f)

            entry = cache.get(str(self.stop_id))
            if entry:
                ts = _parse_iso(entry.get("timestamp"))
                if ts and (datetime.now() - ts < timedelta(days=CACHE_EXPIRY_DAYS)):
                    self.directions = entry.get("directions", [])
                    print("Loaded cached stop {}".format(self.stop_id))
                    return self.directions

        print("Populating stop {} from API...".format(self.stop_id))

        departures = send_ptv_request(
            "/v3/departures/route_type/{}/stop/{}?max_results=5".format(self.route_type, self.stop_id)
        )
        if not departures:
            return []

        direction_ids = []
        for d in departures.get("departures", []):
            did = d.get("direction_id")
            if did and did not in direction_ids:
                direction_ids.append(did)

        for did in direction_ids:
            info = send_ptv_request("/v3/directions/{}".format(did))
            if not info:
                continue

            for direction in info.get("directions", []):
                if direction.get("route_type") != self.route_type:
                    continue

                new_dir = {
                    "direction_id": direction["direction_id"],
                    "direction_name": direction["direction_name"],
                    "route_ids": [direction["route_id"]]
                }

                added = False
                for existing in self.directions:
                    if existing["direction_id"] == new_dir["direction_id"]:
                        rid = new_dir["route_ids"][0]
                        if rid not in existing["route_ids"]:
                            existing["route_ids"].append(rid)
                        added = True
                        break

                if not added:
                    self.directions.append(new_dir)

        # Save to cache
        try:
            if os.path.exists(CACHE_FILE):
                with open(CACHE_FILE, "r") as f:
                    cache = json.load(f)
            else:
                cache = {}

            cache[str(self.stop_id)] = {
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "directions": self.directions
            }

            with open(CACHE_FILE, "w") as f:
                json.dump(cache, f, indent=2)

            print("Cached stop {}".format(self.stop_id))

        except Exception as e:
            print("Warning: failed to save cache ({})".format(e))

        return self.directions