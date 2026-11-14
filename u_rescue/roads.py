"""Download and cache a routable road extract from the public Overpass API."""
import json
from datetime import datetime, timezone
import time
import urllib.parse
import urllib.request
from urllib.error import HTTPError
from pathlib import Path
import networkx as nx
import numpy as np

OVERPASS = "https://overpass-api.de/api/interpreter"

def _fetch_bbox(west,south,east,north,depth=0):
    query = f'[out:json][timeout:180];(way[highway~"^(trunk|primary|secondary|tertiary|unclassified|residential|living_street|road|service|pedestrian|footway|path|steps|track|cycleway)$"]({south},{west},{north},{east}););(._;>;);out body;'
    request = urllib.request.Request(OVERPASS, data=urllib.parse.urlencode({"data":query}).encode(),
        headers={"User-Agent":"U-RESCUE/0.1 (flood decision-support prototype)"})
    try:
        with urllib.request.urlopen(request, timeout=210) as response:
            data=json.loads(response.read())
        return data.get("elements",[])
    except Exception as exc:
        if isinstance(exc,HTTPError) and exc.code not in (502,503,504):
            raise
        if depth>=3 or (east-west)<.08 or (north-south)<.08:
            raise
        midx,midy=(west+east)/2,(south+north)/2
        merged={}
        for box in [(west,south,midx,midy),(midx,south,east,midy),(west,midy,midx,north),(midx,midy,east,north)]:
            time.sleep(1)
            for element in _fetch_bbox(*box,depth+1):
                merged[(element["type"],element["id"])]=element
        return list(merged.values())

def load_roads(cache, bbox):
    cache = Path(cache)
    cache.parent.mkdir(parents=True, exist_ok=True)
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    west, south, east, north = bbox
    elements=_fetch_bbox(west,south,east,north)
    data={"elements":elements}
    data["_u_rescue"] = {"source":OVERPASS, "bbox":[west,south,east,north],
        "acquired_utc":datetime.now(timezone.utc).isoformat()}
    cache.write_text(json.dumps(data), encoding="utf-8")
    return data

def graph_from_osm(data):
    nodes = {e["id"]:(e["lon"],e["lat"]) for e in data.get("elements",[]) if e["type"] == "node"}
    graph = nx.MultiDiGraph()
    for element in data.get("elements",[]):
        if element["type"] != "way":
            continue
        tags, refs = element.get("tags",{}), element.get("nodes",[])
        if tags.get("access") in ("no","private") or tags.get("foot") in ("no","private"):
            continue
        for u,v in zip(refs,refs[1:]):
            if u not in nodes or v not in nodes:
                continue
            a,b = nodes[u],nodes[v]
            mean_lat=np.radians((a[1]+b[1])/2)
            length = 111320*(((a[0]-b[0])*np.cos(mean_lat))**2+(a[1]-b[1])**2)**.5
            raw_speed = str(tags.get("maxspeed","30")).split()[0]
            speed = float(raw_speed) if raw_speed.isdigit() else 30.0
            attrs = {"length_m":length,"highway":tags.get("highway","road"),"name":tags.get("name",""),
                "geometry":[a,b],"access":tags.get("access","unknown"),"speed_kmh":speed}
            # This graph is for pedestrian evacuation. Vehicle one-way rules do
            # not make a public road one-way for foot travel.
            graph.add_edge(u,v,**attrs)
            graph.add_edge(v,u,**{**attrs,"geometry":[b,a]})
    return graph,nodes
