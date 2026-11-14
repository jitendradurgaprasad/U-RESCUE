"""Low-volume walking routes from the public FOSSGIS Valhalla demo service."""
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ENDPOINT = "https://valhalla1.openstreetmap.de/route"

def walking_route(start, end):
    """Return a pedestrian route as GeoJSON coordinates and metres."""
    payload = {
        "locations": [
            {"lat": float(start[1]), "lon": float(start[0]), "type": "break"},
            {"lat": float(end[1]), "lon": float(end[0]), "type": "break"},
        ],
        "costing": "pedestrian",
        "units": "kilometers",
        "format": "osrm",
        "shape_format": "geojson",
        "directions_type": "none",
    }
    url = ENDPOINT + "?" + urlencode({"json": json.dumps(payload, separators=(",", ":"))})
    request = Request(url, headers={
        "User-Agent": "U-RESCUE/0.1 (local educational prototype)",
        "X-Client-Id": "U-RESCUE-local-prototype",
    })
    try:
        with urlopen(request, timeout=20) as response:
            data = json.loads(response.read())
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError("The public walking-route service is temporarily unavailable.") from exc
    routes = data.get("routes") or []
    if not routes:
        message = data.get("message") or data.get("trip", {}).get("status_message") or "No mapped walking route connects these points."
        raise RuntimeError(message)
    route = routes[0]
    geometry = route.get("geometry")
    coordinates = geometry.get("coordinates") if isinstance(geometry, dict) else geometry
    if not coordinates:
        raise RuntimeError("The walking-route service returned no path geometry.")
    return {"coordinates": coordinates, "distance_m": float(route.get("distance", 0)),
            "duration_s": float(route.get("duration", 0)), "source": "OpenStreetMap via FOSSGIS Valhalla"}
